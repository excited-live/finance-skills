#!/usr/bin/env python3
"""Estimate Thai personal income tax (tax year 2026). Estimate only, not a filing."""
from __future__ import annotations

import argparse
import json

BRACKETS = [
    (150_000, 0.00),
    (300_000, 0.05),
    (500_000, 0.10),
    (750_000, 0.15),
    (1_000_000, 0.20),
    (2_000_000, 0.25),
    (5_000_000, 0.30),
    (float("inf"), 0.35),
]

OTHER_EXPENSE = {"freelance": 0.30, "copyright": 0.50, "contractor": 0.30, "medical": 0.60}
PERSONAL_ALLOWANCE = 60_000
EMPLOYMENT_DEDUCTION_CAP = 100_000
RETIREMENT_CAP = 500_000
INSURANCE_CAP = 100_000


def progressive(taxable: float) -> tuple[float, list[dict]]:
    tax = 0.0
    lower = 0.0
    rows = []
    for up_to, rate in BRACKETS:
        if taxable <= lower:
            break
        slice_top = min(taxable, up_to)
        amount = max(slice_top - lower, 0.0)
        slice_tax = amount * rate
        if amount > 0:
            rows.append({"from": lower, "to": slice_top, "rate": rate, "tax": round(slice_tax, 2)})
        tax += slice_tax
        lower = up_to
    return tax, rows


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--employment", type=float, default=0.0)
    p.add_argument("--other", type=float, default=0.0)
    p.add_argument("--other-type", choices=sorted(OTHER_EXPENSE), default="freelance")
    p.add_argument("--allowances", type=float, default=0.0, help="spouse/children/parents, excluding the 60k personal allowance")
    p.add_argument("--retirement", type=float, default=0.0)
    p.add_argument("--insurance", type=float, default=0.0)
    p.add_argument("--donations", type=float, default=0.0)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)

    employment_deduction = min(a.employment * 0.5, EMPLOYMENT_DEDUCTION_CAP)
    other_deduction = a.other * OTHER_EXPENSE[a.other_type]
    retirement = min(a.retirement, RETIREMENT_CAP)
    insurance = min(a.insurance, INSURANCE_CAP)

    income = a.employment + a.other
    after_deductions = max(income - employment_deduction - other_deduction, 0.0)
    donations = min(a.donations, after_deductions * 0.10)
    taxable = max(
        after_deductions - PERSONAL_ALLOWANCE - a.allowances - retirement - insurance - donations,
        0.0,
    )

    tax, rows = progressive(taxable)
    marginal = next((r["rate"] for r in rows[::-1]), 0.0)
    result = {
        "year": 2026,
        "income": round(income, 2),
        "deductions": {
            "employment": round(employment_deduction, 2),
            "other": round(other_deduction, 2),
            "personalAllowance": PERSONAL_ALLOWANCE,
            "allowances": a.allowances,
            "retirement": round(retirement, 2),
            "insurance": round(insurance, 2),
            "donations": round(donations, 2),
        },
        "taxableIncome": round(taxable, 2),
        "tax": round(tax, 2),
        "effectiveRate": round(tax / income, 4) if income else 0.0,
        "marginalRate": marginal,
        "brackets": rows,
        "disclaimer": "Estimate for planning only. Not tax advice and not a filing.",
    }

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"Income            {result['income']:>12,.0f}")
    print(f"Taxable income    {result['taxableIncome']:>12,.0f}")
    print(f"Tax               {result['tax']:>12,.0f}")
    print(f"Effective rate    {result['effectiveRate'] * 100:>11.2f}%")
    print(f"Marginal rate     {result['marginalRate'] * 100:>11.0f}%")


if __name__ == "__main__":
    raise SystemExit(main())
