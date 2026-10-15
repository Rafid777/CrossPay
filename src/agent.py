"""CrossPay Gemini AI agent with stateful chat and 2-step confirmation."""
from google import genai
from src.tool_registry import TOOL_DECLARATIONS, dispatch_tool

_SYSTEM_PROMPT = """You are CrossPay, an AI financial assistant for international students studying in China.
You help students with: FX rate lookups, tuition payment optimization, cross-border remittance comparison, living expense tracking, and credit score building.

RULES YOU MUST FOLLOW:
1. NEVER calculate money amounts yourself. Always call the appropriate tool.
2. For any action that moves money or changes records, always present a clear preview and ask the user to confirm before proceeding.
3. When a tool returns confirmation_required=True, present the details and say "Please confirm or cancel."
4. Always mention the data source and timestamp when quoting FX rates.
5. If check_aml_threshold returns flagged=True, explain the compliance hold clearly.
6. If check_sanctioned_destination returns blocked=True, refuse the transfer and explain why.
7. Be concise, friendly, and use emojis sparingly.
8. Format currency amounts clearly with currency codes (e.g. 8,000 CNY, $500 USD)."""


class CrossPayAgent:
    """Stateful Gemini-powered financial assistant for international students."""

    def __init__(self, student_id: str, api_key: str):
        self.student_id = student_id
        self.api_key = api_key
        self.previous_interaction_id: str | None = None
        self.pending_action: dict | None = None
        self._client = genai.Client(api_key=api_key)

    def _system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    def chat(self, user_message: str) -> str:
        """Send a message, resolve tool calls, return text response."""
        create_kwargs = dict(
            model="gemini-3.8-flash",
            input=user_message,
            system_instruction=self._system_prompt(),
            tools=TOOL_DECLARATIONS,
        )
        if self.previous_interaction_id:
            create_kwargs["previous_interaction_id"] = self.previous_interaction_id

        interaction = self._client.interactions.create(**create_kwargs)
        self.previous_interaction_id = interaction.id

        for step in interaction.steps:
            step_type = getattr(step, "type", None)
            if step_type == "function_call":
                tool_name = step.name
                tool_args = dict(step.arguments) if step.arguments else {}
                result = dispatch_tool(tool_name, tool_args)
                if isinstance(result, dict) and result.get("confirmation_required"):
                    self.pending_action = {"tool": tool_name, "args": tool_args, "preview": result}
                    return self._format_confirmation_preview(tool_name, result)

        return interaction.output_text or "I'm here to help!"

    def confirm_action(self) -> str:
        """Execute the pending write action after user confirmation."""
        if self.pending_action is None:
            return "There is no pending action to confirm."
        tool = self.pending_action["tool"]
        args = self.pending_action["args"]
        self.pending_action = None
        commit_map = {"add_expense": "commit_add_expense", "set_budget_category": "commit_set_budget_category"}
        commit_tool = commit_map.get(tool, tool)
        result = dispatch_tool(commit_tool, args)
        return f"\u2705 Done! Action completed.\n\nDetails: {result}"

    def cancel_action(self) -> str:
        """Cancel the pending write action."""
        self.pending_action = None
        return "Action cancelled. Nothing was changed."

    def _format_confirmation_preview(self, tool_name: str, preview: dict) -> str:
        """Format pending action as human-readable confirmation request."""
        lines = ["\u26a0\ufe0f **Action requires your confirmation:**\n"]
        if tool_name == "add_expense":
            lines += [
                "\U0001f4b0 **Record Expense**",
                f"  Amount: {preview.get('amount_cny', '?')} CNY",
                f"  Category: {preview.get('category', '?')}",
                f"  Note: {preview.get('note', '')}",
                f"  New balance after: {preview.get('new_balance_cny', '?')} CNY",
            ]
        elif tool_name == "set_budget_category":
            lines += [
                "\U0001f4ca **Set Budget Limit**",
                f"  Category: {preview.get('category', '?')}",
                f"  New limit: {preview.get('new_limit_cny', '?')} CNY/month",
            ]
        elif tool_name == "schedule_tuition_payment":
            lines += [
                "\U0001f393 **Schedule Tuition Payment**",
                f"  Amount: {preview.get('amount_cny', '?')} CNY",
                f"  Optimal window: {preview.get('optimal_window', '?')}",
                f"  Projected rate: {preview.get('projected_rate', '?')}",
                f"  Estimated savings: ${preview.get('estimated_savings_usd', '?')} USD",
            ]
        else:
            for k, v in preview.items():
                if k != "confirmation_required":
                    lines.append(f"  {k}: {v}")
        lines.append("\nClick **Confirm** to proceed or **Cancel** to abort.")
        return "\n".join(lines)
