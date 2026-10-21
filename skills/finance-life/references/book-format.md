# Book format

One JSON file, written by `scripts/finance.py`, read by nothing else unless the user
copies it. Every record has a stable `id` so the app importer can map it later.

```json
{
  "format": "finance-life/book",
  "version": 1,
  "currency": "THB",
  "createdAt": "2026-10-21T14:00:00+00:00",
  "entities": [
    { "id": "uuid", "name": "Personal", "type": "personal", "currency": "THB", "targetSafetyBuffer": 6 }
  ],
  "cash": [
    { "id": "uuid", "entityId": "uuid", "name": "KBank", "balance": 120000, "asOf": "2026-10-21" }
  ],
  "incomes": [
    { "id": "uuid", "entityId": "uuid", "name": "Salary", "amount": 60000, "frequency": "monthly", "kind": "employment" }
  ],
  "expenses": [
    { "id": "uuid", "entityId": "uuid", "name": "Rent", "amount": 18000, "frequency": "monthly" }
  ],
  "liabilities": [
    { "id": "uuid", "entityId": "uuid", "name": "Car loan", "balance": 400000, "payment": 9500 }
  ]
}
```

## Rules

- `type`: `personal` (exactly one), `business`, `job`.
- `frequency`: `monthly`, `annual` (÷12), `seasonal` (annual total ÷12), `one_off` (excluded).
- Amounts are in `currency`, positive, no separators.
- Runway = cash ÷ (expenses + debt payments − income), per entity. `null` means
  cash-flow positive (income covers costs).
- Combined runway uses the sum of entity burns, so a profitable business offsets a
  loss-making one. That is intentional: money is fungible across the person's life.

## Mapping to excited.live

The export bundle is `format: excited.live/accounting-import`, `version: 1`, with the
book under `book` and the computed `summary` beside it. The app's book schema lives in
`docs/accounting-data-model.md` (entities, cash assets, incomes, expenses, liabilities);
an importer maps `entities` 1:1, `cash` to `accounting_cash_assets`, `incomes` to
`accounting_incomes`, `expenses` to `accounting_expenses`, `liabilities` to
`accounting_liabilities`. Version the bundle before changing any key: old exports must
stay importable.
