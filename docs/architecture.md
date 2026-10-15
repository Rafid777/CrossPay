# CrossPay System Architecture

## ASCII Overview

```
╔══════════════════════════════════════════════════════════════════╗
║                 CrossPay Architecture                            ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ┌──────────────────────────────────────────────────────────┐   ║
║  │              PRESENTATION LAYER                           │   ║
║  │  app.py (Streamlit)  +  src/ui_components.py             │   ║
║  │  • Chat interface    • Sidebar (stats, quick actions)    │   ║
║  │  • Confirmation banner (Confirm/Cancel buttons)          │   ║
║  └─────────────────────────┬────────────────────────────────┘   ║
║                            │                                     ║
║  ┌─────────────────────────▼────────────────────────────────┐   ║
║  │                 AGENT LAYER                               │   ║
║  │  src/agent.py — CrossPayAgent                            │   ║
║  │  • Gemini 3.8 Flash (function-calling)                   │   ║
║  │  • Stateful: previous_interaction_id                     │   ║
║  │  • Tool call loop + confirmation gate                    │   ║
║  └────────┬─────────────────────────────┬────────────────────┘   ║
║           │                             │                        ║
║  ┌────────▼──────────┐      ┌───────────▼────────────────────┐   ║
║  │  GEMINI API       │      │  TOOL REGISTRY                 │   ║
║  │  gemini-3.8-flash │      │  src/tool_registry.py          │   ║
║  │  (LLM reasoning,  │      │  • TOOL_DECLARATIONS (10 tools)│   ║
║  │   function calls) │      │  • dispatch_tool() router      │   ║
║  └───────────────────┘      └───────────┬────────────────────┘   ║
║                                         │                        ║
║  ┌──────────────────────────────────────▼─────────────────────┐  ║
║  │                    TOOLS LAYER                              │  ║
║  │  src/tools/                                                 │  ║
║  │  ┌──────────┐ ┌───────────┐ ┌────────┐ ┌───────────────┐  │  ║
║  │  │  fx.py   │ │remittance │ │budget  │ │  compliance   │  │  ║
║  │  │ FX rates │ │ .py       │ │ .py    │ │   .py         │  │  ║
║  │  │ convert  │ │ compare   │ │ track  │ │ AML│sanctions │  │  ║
║  │  └──────────┘ └───────────┘ └────────┘ │ PII masking  │  │  ║
║  │  ┌──────────┐                           └───────────────┘  │  ║
║  │  │credit.py │                                               │  ║
║  │  │ profile  │                                               │  ║
║  │  │ simulate │                                               │  ║
║  │  └──────────┘                                               │  ║
║  └──────────────────────────────┬──────────────────────────────┘  ║
║                                 │                                 ║
║  ┌──────────────────────────────▼──────────────────────────────┐  ║
║  │               DATA & AUDIT LAYER                             │  ║
║  │  src/logger.py          src/db.py                           │  ║
║  │  logs/execution_log.jsonl    data/crosspay.db (SQLite)      │  ║
║  │  (PII-masked audit trail)    (accounts, expenses, budgets)  │  ║
║  └─────────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════╝
```

## Mermaid Diagram

```mermaid
flowchart TD
    U([User]) --> APP[Streamlit App\napp.py]
    APP --> CONF{pending_action?}
    CONF -->|Yes| BANNER[Confirmation Banner\nConfirm / Cancel]
    CONF -->|No| CHAT[Chat Input]
    BANNER --> AGENT
    CHAT --> AGENT[CrossPayAgent\nsrc/agent.py]
    AGENT --> GEMINI[Gemini 3.8 Flash\nFunction Calling]
    GEMINI -->|function_call step| DISPATCH[dispatch_tool\nsrc/tool_registry.py]
    DISPATCH --> LOG[log_tool_call\nlogs/execution_log.jsonl]
    DISPATCH --> T0[Tier 0 Tools\nRead-Only\nFX, Remittance, Credit]
    DISPATCH --> T1[Tier 1 Tools\nWrite Preview\nadd_expense, set_budget]
    DISPATCH --> T2[Tier 2 Tools\nRegulated\ntuition, AML, sanctions]
    T1 -->|confirmation_required=True| CONF
    T2 -->|confirmation_required=True| CONF
    T0 --> DB[(SQLite DB\ncrosspay.db)]
    T1 --> DB
    T2 --> DB
```
