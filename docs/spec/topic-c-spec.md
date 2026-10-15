# Topic C Specification: Cross-border & Student Finance Assistant

## Source
WeBank International AI Finance Challenge, October 2026

## Problem Statement
International students studying in China face significant friction managing cross-border finances: high FX markups when paying tuition, opaque remittance fees, difficulty tracking multi-currency expenses, and inability to build a credit history in a new country.

## Requirements
1. **FX Rate Lookup**: Provide real-time (or reliably mocked) exchange rates between home currencies (BDT, PKR, NGN) and CNY with fee transparency.
2. **Remittance Comparison**: Compare at least 3 cross-border payment providers by total cost (fee + FX markup).
3. **Tuition Payment Optimization**: Suggest optimal timing windows for tuition transfers based on FX patterns.
4. **Budget Tracking**: Track living expenses by category in CNY with budget limits.
5. **Credit Building**: Provide actionable credit-building guidance tailored to international students.
6. **Compliance**: AML threshold checking ($10,000 USD), sanctioned destination screening, PII protection.
7. **Security**: All write actions require explicit 2-step confirmation. Audit log of all tool invocations.
