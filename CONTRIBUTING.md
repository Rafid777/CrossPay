# Contributing to CrossPay (微众智汇)

Thank you for your interest in contributing to **CrossPay**! As an enterprise fintech project for the WeBank International AI Finance Challenge, we maintain strict architectural and regulatory standards.

## Core Architectural Invariants

Every contribution must honor our three non-negotiable invariants:

1. **Zero-Arithmetic-Hallucination**:
   - The Large Language Model (Gemini) must **never** calculate financial values, exchange rates, fee totals, or compliance limits directly.
   - All numerical computations must reside inside pure deterministic Python tools in `src/tools/`.
2. **Two-Step Confirmation for State Mutation**:
   - Any tool that updates student balances, sets budget thresholds, or registers tuition schedules must require explicit user confirmation.
   - Preview functions must return `{"confirmation_required": True}` and halt execution until the user clicks **Confirm**.
3. **Data Privacy & PII Protection**:
   - No plaintext bank account numbers (8+ digits) or passport numbers may ever be written to disk or logs.
   - All logged inputs and outputs must pass through `mask_pii()`.

## Development Workflow

1. Fork the repository and create a descriptive branch:
   ```bash
   git checkout -b feat/indonesia-idr-corridor
   ```
2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Implement tests first following Test-Driven Development (TDD).
4. Run the full test suite and ensure 100% pass rate:
   ```bash
   python -m pytest tests/ -v
   ```
5. Submit a pull request with the completed PR checklist.
