#!/usr/bin/env python3
"""finance-life: a local, file-based book for one person's whole financial life.

Every command reads and writes a single JSON file (default ~/finance/book.json)
in the format documented in references/book-format.md. Nothing leaves the machine
except an explicit `export`, which writes a file the user can hand to the app.

Commands
  init [--home DIR] [--currency THB]
  entity add --name NAME --type personal|business|job [--buffer 6]
  cash set --entity NAME --name LABEL --balance N [--as-of YYYY-MM-DD]
  income add --entity NAME --name LABEL --amount N [--frequency monthly|annual|seasonal|one_off]
  expense add --entity NAME --name LABEL --amount N [--frequency monthly|annual|one_off]
  liability add --entity NAME --name LABEL --balance N [--payment N]
  snapshot [--json]
  export [--out PATH]
  check
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

DEFAULT_HOME = Path(os.environ.get("FINANCE_HOME", Path.home() / "finance"))
BOOK_NAME = "book.json"
FREQUENCIES = ("monthly", "annual", "seasonal", "one_off")
ENTITY_TYPES = ("personal", "business", "job")


# ---------------------------------------------------------------- storage

def book_path(home: Path | None = None) -> Path:
    return (home or DEFAULT_HOME) / BOOK_NAME


def load(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"no book at {path}. Run: finance.py init")
    with path.open(encoding="utf-8") as fh:
        book = json.load(fh)
    book.setdefault("entities", [])
    book.setdefault("cash", [])
    book.setdefault("incomes", [])
    book.setdefault("expenses", [])
    book.setdefault("liabilities", [])
    return book


def save(path: Path, book: dict) -> None:
    book["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(book, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    tmp.replace(path)


def new_id() -> str:
    return str(uuid.uuid4())


def entity_by_name(book: dict, name: str) -> dict:
    for e in book["entities"]:
        if e["name"].strip().lower() == name.strip().lower():
            return e
    names = ", ".join(e["name"] for e in book["entities"]) or "none"
    sys.exit(f"unknown entity {name!r}. Known: {names}")


# ---------------------------------------------------------------- maths

def monthly(amount: float, frequency: str) -> float:
    if frequency == "monthly":
        return amount
    if frequency == "annual":
        return amount / 12.0
    if frequency == "seasonal":
        return amount / 12.0  # a seasonal total is averaged over the year
    return 0.0  # one_off is excluded from the recurring picture


def entity_summary(book: dict, entity: dict) -> dict:
    eid = entity["id"]
    cash = sum(c["balance"] for c in book["cash"] if c["entityId"] == eid)
    income = sum(monthly(i["amount"], i.get("frequency", "monthly")) for i in book["incomes"] if i["entityId"] == eid)
    expenses = sum(monthly(x["amount"], x.get("frequency", "monthly")) for x in book["expenses"] if x["entityId"] == eid)
    debt_service = sum(l.get("payment", 0) for l in book["liabilities"] if l["entityId"] == eid)
    burn = expenses + debt_service - income
    if burn <= 0:
        runway = None
    else:
        runway = round(cash / burn, 1) if cash > 0 else 0.0
    buffer = entity.get("targetSafetyBuffer") or 0
    return {
        "entity": entity["name"],
        "type": entity["type"],
        "cash": round(cash, 2),
        "monthlyIncome": round(income, 2),
        "monthlyExpenses": round(expenses, 2),
        "debtService": round(debt_service, 2),
        "monthlyBurn": round(burn, 2),
        "runwayMonths": runway,
        "targetBufferMonths": buffer,
        "bufferGapMonths": (round(buffer - (runway or 0), 1) if buffer else None),
    }


def summarise(book: dict) -> dict:
    rows = [entity_summary(book, e) for e in book["entities"]]
    total_cash = round(sum(r["cash"] for r in rows), 2)
    total_income = round(sum(r["monthlyIncome"] for r in rows), 2)
    total_burn = round(sum(r["monthlyBurn"] for r in rows), 2)
    return {
        "currency": book.get("currency", "THB"),
        "entities": rows,
        "combined": {
            "cash": total_cash,
            "monthlyIncome": total_income,
            "monthlyBurn": total_burn,
            "runwayMonths": (round(total_cash / total_burn, 1) if total_burn > 0 and total_cash > 0 else None),
        },
        "asOf": date.today().isoformat(),
    }


# ---------------------------------------------------------------- commands

def cmd_init(args):
    path = book_path(Path(args.home) if args.home else None)
    if path.exists() and not args.force:
        print(f"book already exists: {path}")
        return
    book = {
        "format": "finance-life/book",
        "version": 1,
        "currency": args.currency,
        "createdAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "entities": [],
        "cash": [],
        "incomes": [],
        "expenses": [],
        "liabilities": [],
    }
    save(path, book)
    print(f"created {path}")


def cmd_entity_add(args):
    path = book_path()
    book = load(path)
    if any(e["name"].strip().lower() == args.name.strip().lower() for e in book["entities"]):
        sys.exit(f"entity {args.name!r} already exists")
    if args.type == "personal" and any(e["type"] == "personal" for e in book["entities"]):
        sys.exit("a book has exactly one personal entity")
    book["entities"].append(
        {
            "id": new_id(),
            "name": args.name,
            "type": args.type,
            "currency": book.get("currency", "THB"),
            "targetSafetyBuffer": args.buffer,
        }
    )
    save(path, book)
    print(f"added {args.type} entity {args.name!r}")


def cmd_cash_set(args):
    path = book_path()
    book = load(path)
    ent = entity_by_name(book, args.entity)
    row = next((c for c in book["cash"] if c["entityId"] == ent["id"] and c["name"] == args.name), None)
    if row:
        row["balance"] = args.balance
        row["asOf"] = args.as_of
    else:
        book["cash"].append(
            {"id": new_id(), "entityId": ent["id"], "name": args.name, "balance": args.balance, "asOf": args.as_of}
        )
    save(path, book)
    print(f"{args.entity}/{args.name}: {args.balance:,.0f} {book.get('currency', 'THB')} as of {args.as_of}")


def _add_flow(args, kind: str):
    path = book_path()
    book = load(path)
    ent = entity_by_name(book, args.entity)
    book[kind].append(
        {
            "id": new_id(),
            "entityId": ent["id"],
            "name": args.name,
            "amount": args.amount,
            "frequency": args.frequency,
            "kind": "employment" if args.employment else "business",
        }
        if kind == "incomes"
        else {
            "id": new_id(),
            "entityId": ent["id"],
            "name": args.name,
            "amount": args.amount,
            "frequency": args.frequency,
        }
    )
    save(path, book)
    print(f"{kind[:-1]}: {args.name} {args.amount:,.0f}/{args.frequency} under {args.entity}")


def cmd_income_add(args):
    _add_flow(args, "incomes")


def cmd_expense_add(args):
    _add_flow(args, "expenses")


def cmd_liability_add(args):
    path = book_path()
    book = load(path)
    ent = entity_by_name(book, args.entity)
    book["liabilities"].append(
        {"id": new_id(), "entityId": ent["id"], "name": args.name, "balance": args.balance, "payment": args.payment}
    )
    save(path, book)
    print(f"liability: {args.name} balance {args.balance:,.0f}, payment {args.payment:,.0f}/mo")


def cmd_snapshot(args):
    data = summarise(load(book_path()))
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    cur = data["currency"]
    for r in data["entities"]:
        runway = "cash-flow positive" if r["runwayMonths"] is None else f"{r['runwayMonths']:.1f} months"
        print(
            f"{r['entity']:<22} {cur} {r['cash']:>12,.0f} cash  "
            f"in {r['monthlyIncome']:>9,.0f}  out {r['monthlyExpenses'] + r['debtService']:>9,.0f}  runway {runway}"
        )
    c = data["combined"]
    total_runway = "cash-flow positive" if c["runwayMonths"] is None else f"{c['runwayMonths']:.1f} months"
    print(f"{'COMBINED':<22} {cur} {c['cash']:>12,.0f} cash  runway {total_runway}")


def cmd_export(args):
    book = load(book_path())
    bundle = {
        "format": "excited.live/accounting-import",
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "github.com/excited-live/finance-skills",
        "book": book,
        "summary": summarise(book),
    }
    out = Path(args.out) if args.out else book_path().with_name("excited-import.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    print("The app can import this file. Nothing was uploaded.")


def cmd_check(_args):
    path = book_path()
    book = load(path)
    problems = []
    ids = set()
    for e in book["entities"]:
        if e["id"] in ids:
            problems.append(f"duplicate id {e['id']}")
        ids.add(e["id"])
    known = {e["id"] for e in book["entities"]}
    for section in ("cash", "incomes", "expenses", "liabilities"):
        for row in book[section]:
            if row["entityId"] not in known:
                problems.append(f"{section} {row.get('name')!r} points at unknown entity")
    if not any(e["type"] == "personal" for e in book["entities"]):
        problems.append("no personal entity")
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print(f"ok: {len(book['entities'])} entities, {sum(len(book[s]) for s in ('cash', 'incomes', 'expenses', 'liabilities'))} rows")


def main(argv=None):
    p = argparse.ArgumentParser(prog="finance.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init")
    s.add_argument("--home")
    s.add_argument("--currency", default="THB")
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("entity")
    es = s.add_subparsers(dest="entity_cmd", required=True)
    a = es.add_parser("add")
    a.add_argument("--name", required=True)
    a.add_argument("--type", required=True, choices=ENTITY_TYPES)
    a.add_argument("--buffer", type=float, default=None)
    a.set_defaults(fn=cmd_entity_add)

    s = sub.add_parser("cash")
    cs = s.add_subparsers(dest="cash_cmd", required=True)
    a = cs.add_parser("set")
    a.add_argument("--entity", required=True)
    a.add_argument("--name", required=True)
    a.add_argument("--balance", type=float, required=True)
    a.add_argument("--as-of", default=date.today().isoformat())
    a.set_defaults(fn=cmd_cash_set)

    s = sub.add_parser("income")
    ins = s.add_subparsers(dest="income_cmd", required=True)
    a = ins.add_parser("add")
    a.add_argument("--entity", required=True)
    a.add_argument("--name", required=True)
    a.add_argument("--amount", type=float, required=True)
    a.add_argument("--frequency", choices=FREQUENCIES, default="monthly")
    a.add_argument("--employment", action="store_true")
    a.set_defaults(fn=cmd_income_add)

    s = sub.add_parser("expense")
    ex = s.add_subparsers(dest="expense_cmd", required=True)
    a = ex.add_parser("add")
    a.add_argument("--entity", required=True)
    a.add_argument("--name", required=True)
    a.add_argument("--amount", type=float, required=True)
    a.add_argument("--frequency", choices=FREQUENCIES, default="monthly")
    a.set_defaults(fn=cmd_expense_add)

    s = sub.add_parser("liability")
    ls = s.add_subparsers(dest="liability_cmd", required=True)
    a = ls.add_parser("add")
    a.add_argument("--entity", required=True)
    a.add_argument("--name", required=True)
    a.add_argument("--balance", type=float, required=True)
    a.add_argument("--payment", type=float, default=0.0)
    a.set_defaults(fn=cmd_liability_add)

    s = sub.add_parser("snapshot")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_snapshot)

    s = sub.add_parser("export")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_export)

    sub.add_parser("check").set_defaults(fn=cmd_check)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
