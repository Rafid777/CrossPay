#!/usr/bin/env python
"""Generate execution evidence by running scripted tool calls.

This script demonstrates all CrossPay tool categories and produces
the audit log for competition Deliverable 06.

Usage:
    python scripts/generate_execution_evidence.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from src.db import get_db
from src.mock_data import seed_mock_data
from src.tool_registry import dispatch_tool

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def main():
    # Seed DB
    conn = get_db()
    seed_mock_data(conn)
    conn.close()
    print("[CrossPay] DB seeded. Running scripted tool calls...\n")

    scenarios = [
        (
            "get_exchange_rate",
            {"from_currency": "BDT", "to_currency": "CNY"},
            "FX: BDT → CNY rate lookup"
        ),
        (
            "convert_amount",
            {"amount": 50000.0, "from_currency": "BDT", "to_currency": "CNY"},
            "FX: Convert 50,000 BDT to CNY (tuition equivalent)"
        ),
        (
            "compare_remittance_options",
            {"amount_usd": 400.0, "destination_country": "CN"},
            "Remittance: Compare providers for $400 USD transfer to China"
        ),
        (
            "schedule_tuition_payment",
            {"student_id": "STU001", "amount_cny": 8000.0, "due_date": "2026-11-01"},
            "Remittance: Schedule tuition payment (preview — confirmation_required)"
        ),
        (
            "get_spending_summary",
            {"student_id": "STU001", "month": "2026-10"},
            "Budget: Monthly spending summary for STU001"
        ),
        (
            "get_credit_profile",
            {"student_id": "STU001"},
            "Credit: Credit profile for STU001 (score 680, Good tier)"
        ),
        (
            "check_aml_threshold",
            {"amount_usd": 12500.0},
            "Compliance: AML check — $12,500 USD (FLAGGED)"
        ),
        (
            "check_sanctioned_destination",
            {"country_code": "IR"},
            "Compliance: Sanctions check — Iran (BLOCKED)"
        ),
        (
            "get_fx_trend",
            {"from_currency": "BDT", "days": 30},
            "Analytics: 30-day BDT/CNY historical exchange rate trend"
        ),
        (
            "get_spending_trend",
            {"student_id": "STU001", "months": 6},
            "Analytics: 6-month categorical living expense trend"
        ),
        (
            "get_credit_trend",
            {"student_id": "STU001"},
            "Analytics: 6-month credit score progression trajectory"
        ),
        (
            "get_worldbank_remittance",
            {"country": "Bangladesh", "flow": "outflow", "year": 2023},
            "World Bank: Official remittance macro outflows for Bangladesh (2023)"
        ),
    ]

    results = []
    for tool_name, args, description in scenarios:
        try:
            result = dispatch_tool(tool_name, args)
            status = "✅ OK"
            # Brief result summary
            if isinstance(result, dict):
                if result.get("flagged") or result.get("blocked"):
                    status = "🚩 FLAGGED/BLOCKED"
                elif result.get("confirmation_required"):
                    status = "⚠️  CONFIRM REQUIRED"
                summary = str(result)[:80] + "..." if len(str(result)) > 80 else str(result)
            elif isinstance(result, list):
                summary = f"{len(result)} providers returned"
            else:
                summary = str(result)[:80]
        except Exception as e:
            status = f"❌ ERROR"
            summary = str(e)[:80]

        results.append((tool_name, description, status, summary))
        print(f"  [{status}] {description}")

    print(f"\n[CrossPay] {len(results)} tool calls logged to logs/execution_log.jsonl")

    if HAS_RICH:
        console = Console()
        table = Table(title="CrossPay Execution Evidence Summary", box=box.ROUNDED)
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Scenario", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Result Preview", style="dim")
        for tool_name, description, status, summary in results:
            table.add_row(tool_name, description, status, summary)
        console.print(table)
    else:
        print("\n--- EXECUTION EVIDENCE SUMMARY ---")
        for tool_name, description, status, summary in results:
            print(f"  {tool_name:35s} | {status:20s} | {description}")

    print("\n✅ Execution evidence generation complete.")
    print("   Audit log: logs/execution_log.jsonl")
    print("   See docs/execution-evidence-summary.md for the full report.")


if __name__ == "__main__":
    main()
