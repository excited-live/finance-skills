---
name: thai-personal-tax
description: Estimate Thai personal income tax for a year from a few numbers.
version: 0.1.0
author: Prame (fromsukong), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [tax, thailand, personal-finance, estimate]
  related_skills: [finance-life]
---

# Thai Personal Tax

Estimate Thai personal income tax (PND 90/91 shape) from employment and other income,
with the standard deductions and allowances most people actually use. This is an
estimate for planning, not a filing.

## When to Use

- "how much tax will I owe this year", "should I take this as salary or freelance"
- Planning a bonus, a side income, or a mid-year rate change
- Don't use for: filing, withholding certificates, VAT, corporate tax, or anything that
  needs a Revenue Department form. Say it is an estimate and point to a filing tool.

## Prerequisites

- Python 3.9+, stdlib only. No network.

## How to Run

```bash
python3 scripts/tax.py --employment 720000 --other 240000 --other-type freelance \
  --allowances 60000 --retirement 200000 --insurance 25000
```

## Quick Reference

```
--employment N        salary + bonus for the year (40(1), 40(2))
--other N             non-employment income (40(3)-40(8))
--other-type freelance|copyright|contractor|medical   expense deduction rate
--allowances N        personal + spouse + children (60k personal is added by default)
--retirement N        SSF/RMF/provident/pension insurance, capped 500k
--insurance N         health/life insurance, capped 100k
--donations N         donations, capped at 10% of income after deductions
--json                machine output
```

## Procedure

1. Collect employment income and other income separately. Done when each has a number.
2. Run the script with the deductions the user actually has. Done when the output shows
   taxable income and tax before credits.
3. Report the marginal bracket and the effective rate, not just the total. Done when the
   user knows what the next 100,000 THB of income would cost.
4. If the answer drives a decision, connect it back: a raise that pushes them into a
   higher bracket may still be worth it, and a side business changes the picture through
   expense deductions.

## Pitfalls

- **Progressive, not flat.** A common wrong answer is to apply the top rate to all income.
  The script applies brackets in order.
- **Employment expense deduction is 50% capped at 100,000.** Applying the full 50% to a
  large salary overstates the deduction.
- **The 500,000 retirement cap is shared** across SSF, RMF, provident fund and pension
  insurance; do not stack them.
- **Allowances are not all cash.** Only claim what the user can document.
- **This is an estimate.** The Revenue Department's own calculation and any withholding
  already paid decide the final number.

## Verification

- Taxable income ≥ 0 and never exceeds total income
- Effective rate ≤ marginal rate
- `--json` output sums: bracket taxes add up to the total

## Source of truth

Brackets and categories follow `excited.live/packages/tax/src/thai/thai-2026.ts`
(tax year 2026). If that file changes, update `references/rates.md` and the script
together; a mismatch is a bug in this skill.
