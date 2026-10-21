# Thai personal income tax rates, tax year 2026

Source of truth: `excited.live/packages/tax/src/thai/thai-2026.ts`. Update this file and
`scripts/tax.py` together.

## Progressive brackets (THB of taxable income)

| Up to | Rate |
| --- | --- |
| 150,000 | 0% |
| 300,000 | 5% |
| 500,000 | 10% |
| 750,000 | 15% |
| 1,000,000 | 20% |
| 2,000,000 | 25% |
| 5,000,000 | 30% |
| above | 35% |

## Deductions modelled here

- Employment income: 50% expense deduction, capped at 100,000
- Non-employment: 40(3) copyright 50% (cap 100,000), 40(6) freelance 30%, medical 60%,
  contractor 30%
- Personal allowance: 60,000
- Retirement pool (SSF, RMF, provident, pension insurance, NSF, GPF): 500,000 combined cap
- Insurance: 100,000 cap
- Donations: 10% of income after deductions

## Not modelled

Minimum alternative tax under Section 48(2), dividend tax credits, withholding already
paid, spouse/parent health insurance specifics, prenatal care, and the 2x donation
deduction for education and public healthcare. Those live in the app's tax package and
change the final liability; say so when a user's case touches them.
