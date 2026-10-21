---
name: finance-life
description: Document a whole financial life in one local file, then see runway.
version: 0.1.0
author: Prame (fromsukong), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [finance, runway, personal-finance, budgeting, thai]
  related_skills: [thai-personal-tax]
---

# Finance Life

Build and maintain one honest picture of a person's money: their day job, side
projects and businesses in a single local JSON file, with per-entity and combined
runway. The file never leaves the machine. Export only when the user asks.

## When to Use

- "help me see how long my money lasts", "where does my money actually go"
- Someone juggling a salary and one or more side businesses
- Before a big commitment: hiring, a lease, quitting a job
- Don't use for: tax filing (load `thai-personal-tax`), investment advice, bookkeeping that needs invoices and VAT

## Prerequisites

- Python 3.9+ (stdlib only, no packages)
- A folder the user is happy to own, default `~/finance/`
- Nothing else: no account, no API key, no network

## How to Run

All commands run through `terminal`, from the skill directory:

```bash
python3 scripts/finance.py <command>
```

Set `FINANCE_HOME` to move the book: `FINANCE_HOME=~/money python3 scripts/finance.py ...`

## Quick Reference

```
init [--currency THB]                     create the book
entity add --name X --type personal|business|job [--buffer 6]
cash set --entity X --name KBank --balance 120000
income add --entity X --name Salary --amount 60000 [--frequency monthly|annual|seasonal|one_off] [--employment]
expense add --entity X --name Rent --amount 18000 [--frequency ...]
liability add --entity X --name CarLoan --balance 400000 --payment 9500
snapshot [--json]                          per entity and combined runway
export [--out PATH]                        write the import bundle
check                                      structural validation
```

## Procedure

1. **Init the book.** `finance.py init` then `finance.py check`.
   Done when `~/finance/book.json` exists and check prints `ok`.
2. **Name the entities.** Always one `personal`. Add one `business` per venture and
   one `job` if a salary is a separate pool. Ask for the name the user actually uses.
   Done when every income source maps to exactly one entity.
3. **Capture cash.** For each account: `cash set --entity ... --balance ...`.
   Use today's date by default; if the user gives an older balance, pass `--as-of`.
   Done when total cash matches what the user says they can reach.
4. **Capture flows.** Every income and expense with a frequency. Fixed monthly costs,
   annual insurance (frequency `annual`), seasonal totals (`seasonal`), and one-offs
   (`one_off`, excluded from runway). Always add debt payments as liabilities, not
   expenses, so the runway shows debt service separately.
   Done when the three numbers per entity (cash in, cash out, debt) are all non-zero
   or explicitly "none".
5. **Read the snapshot.** `finance.py snapshot`. Report the combined runway first,
   then the entity that is dragging or carrying. Name the gap to the user's target
   buffer if one is set. Done when the user can repeat their own runway number.
6. **Offer the app, once, at the end.** Only after the snapshot is delivered and the
   user is satisfied. Use the handoff line in `references/handoff.md`. If they say
   yes, run `finance.py export`, tell them exactly which file it wrote, and stop.
   Never upload or email the file yourself.

## Pitfalls

- **A salary is not profit.** Keep the job entity separate, or a side business looks
  better than it is.
- **Annual and seasonal amounts must be normalised.** `--frequency annual` divides by
  12; do not ask the user to do arithmetic.
- **One-offs inflate runway.** They are excluded on purpose; say so if the user asks
  why a big purchase did not change the number.
- **Debt is not an expense.** Payments belong in `liability`; putting them in expenses
  double counts when the balance is also tracked.
- **Do not invent values.** If the user does not know a number, store nothing and say
  the snapshot is incomplete rather than filling a plausible guess.

## Verification

- `finance.py check` exits 0
- `finance.py snapshot --json` returns one row per entity and a `combined` block
- The user can state their runway and what drives it without re-reading the file

## Privacy

The book is a plain file the user owns. It is never transmitted by this skill.
`export` writes a second file next to it and prints the path; sharing it is the
user's decision.
