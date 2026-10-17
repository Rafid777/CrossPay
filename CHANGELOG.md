# Changelog — CrossPay (微众智汇)

All notable changes to the **CrossPay** platform are documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-10-18
### Added
- **Master Operational Manual (Deliverable 00)**: 10-page publication-grade PDF (`docs/CrossPay_Master_Operational_Manual.pdf`) and markdown companion (`docs/master-operational-manual.md`).
- **PRC Anti-Telecom Fraud & Cybercrime Engine (`src/tools/fraud.py`)**: Tuition discount scam detection, underground P2P screening under PBOC "Card Break Action" (断卡行动), and Action 96110 emergency alerts.
- **Automated Verification Matrix**: Expanded test suite to **152 passing tests** across 16 test suites.
- **Developer & CI/CD Tooling**: GitHub Actions workflows for automated pytest and Bandit/Flake8 security analysis (`.github/workflows/`).
- **Open-Source Health Files**: Added `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE`, and GitHub issue/PR templates.
- **Enterprise Configuration**: Added `pyproject.toml`, `.flake8`, and `setup.cfg` packaging specifications.

### Fixed
- Fixed PBOC central parity quote exception on unsupported currencies with defensive error handling.
- Added non-positive amount boundary guards to remittance and expense scheduling commitments.
- Added currency-aware SAFE facilitation quota conversion for foreign currency transactions.
- Resolved Streamlit cold-start session state bootstrap crash across all 6 pages.
- Registered Adobe `STSong-Light` CID font for native Chinese text rendering in PDF reports.

---

## [2.0.0] - 2026-10-16
### Added
- **6-Page Enterprise Streamlit Application**: Executive Dashboard, AI Assistant, Analytics, Settings, Global Intelligence, and AI Model Studio.
- **Dual Autonomous Intelligence Engine**: Sub-4ms local NLP intent classification alongside Gemini 3.8 Flash hybrid mode.
- **World Bank Macro Integration**: Historical bilateral remittance dataset spanning 221 countries from 2000 to 2024.
- **5,000 Empirical Transactions**: Rich transaction history for statistical cohort benchmarking and Tukey's IQR anomaly detection.
- **Proprietary CrossPay Financial Health Score™**: 4-factor composite financial wellness indicator (0–100).
- **Proactive Smart Alerts Engine**: Automatic notification of tuition payment deadlines, budget limits, and FX opportunities.

---

## [1.0.0] - 2026-10-15
### Added
- Initial project scaffolding, SQLite database, and mock multi-national student seeding.
- Deterministic core financial tools: FX conversion, provider remittance comparison, budget ledger, credit profile, and compliance checks.
- Two-step confirmation gate for all financial database write operations.
- PII-sanitized audit logging (`logs/execution_log.jsonl`).
