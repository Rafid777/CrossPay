"""CrossPay Gemini AI agent with stateful chat and 2-step confirmation."""
from google import genai
from src.tool_registry import TOOL_DECLARATIONS, dispatch_tool

from src.tools.compliance import mask_pii
from src.autonomous_engine import AutonomousFinEngine

_SYSTEM_PROMPT = """You are CrossPay (微众智汇), an intelligent AI financial assistant designed for international students studying in China, powered by WeBank financial infrastructure.
You help students master cross-border finances: foreign exchange rate queries, tuition payment timing optimization, remittance provider comparison, living expense budgeting, and credit score building.

CORE PRINCIPLES & RULES YOU MUST STRICTLY FOLLOW:
1. NEVER calculate monetary amounts yourself. Always call the corresponding deterministic tool function.
2. For any write action that alters balances or records (add_expense, set_budget_category, schedule_tuition_payment), a 2-step confirmation gate is enforced. Always present a structured preview and require user confirmation.
3. When a tool returns confirmation_required=True, summarize the transaction clearly and instruct the student to confirm or cancel.
4. When quoting exchange rates, always state the provider and timestamp from the tool output.
5. If check_aml_threshold returns flagged=True, clearly explain the PBOC/SAFE regulatory reporting requirement ($10,000 USD limit) and necessary documentation.
6. If check_sanctioned_destination returns blocked=True, politely decline the remittance and explain the international sanctions constraint.
7. Multilingual Fluency: Respond fluently in the language the student speaks. If the student asks in Chinese, reply in professional, warm Chinese (简体中文). If in English, reply in clear, professional English.
8. WeBank Advantage: When comparing cross-border remittance methods, objectively highlight WeBank Direct's key strengths (lowest FX markup ~0.8%, next-day settlement, direct UnionPay integration).
9. Format all currency amounts with ISO symbols or codes (e.g., ¥8,000 CNY, $500 USD). Keep tone friendly, professional, and reassuring."""



class CrossPayAgent:
    """Hybrid Autonomous & Gemini-powered financial assistant for international students."""

    def __init__(self, student_id: str, api_key: str = "", engine_mode: str = "auto"):
        self.student_id = student_id
        self.api_key = api_key or ""
        self.engine_mode = engine_mode
        self.previous_interaction_id: str | None = None
        self.pending_action: dict | None = None
        self.autonomous_engine = AutonomousFinEngine(student_id)
        self._client = None
        try:
            if self.api_key:
                self._client = genai.Client(api_key=self.api_key)
        except Exception:
            self._client = None

    def _system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    def chat(self, user_message: str) -> str:
        """Send a message, resolve tool calls, return text response."""
        use_gemini = (
            self.engine_mode == "gemini" or
            (self.engine_mode == "auto" and self._client is not None and self.api_key and self.api_key not in ["demo-placeholder", "none", "local"])
        )

        if not use_gemini:
            resp, pending = self.autonomous_engine.process_query(user_message)
            if pending:
                self.pending_action = pending
            return resp

        try:
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
        except Exception:
            # Fallback seamlessly to local autonomous engine if cloud API call fails
            resp, pending = self.autonomous_engine.process_query(user_message)
            if pending:
                self.pending_action = pending
            return resp

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
