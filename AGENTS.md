# Agents working in this repo

This repository ships Agent Skills. Read this before adding or editing one.

## Layout

```
skills/<name>/SKILL.md      required, the skill itself
skills/<name>/scripts/      executable helpers the skill calls
skills/<name>/references/   detail loaded only when the skill needs it
skills/<name>/templates/    starter files the skill copies
scripts/validate_skills.py  repo validator, runs in CI
```

The directory name must equal the frontmatter `name`. Both are lowercase-hyphenated.

## Rules

- **One skill, one job.** If a skill needs a second workflow that does not share its
  commands, it is a new skill.
- **Scripts do the arithmetic.** Prose tells the agent when to call a script; it never
  asks the model to compute money. Every number a user sees must come from a script.
- **No network, no telemetry, no uploads.** These skills handle the most sensitive data
  a person has. Anything that leaves the machine must be an explicit user action.
- **Never invent a number.** Missing input stays missing; the skill says the picture is
  incomplete.
- **Keep the handoff in one place.** The app offer lives in
  `skills/finance-life/references/handoff.md` and is made once, after value is delivered.
- **Version the data, not the prose.** `book.json` and the export bundle carry a
  `version`. Bump it only for breaking shape changes, and write the migration.

## Before pushing

```bash
python3 scripts/validate_skills.py
FINANCE_HOME=$(mktemp -d) bash -c '
  python3 skills/finance-life/scripts/finance.py init
  python3 skills/finance-life/scripts/finance.py entity add --name Personal --type personal
  python3 skills/finance-life/scripts/finance.py cash set --entity Personal --name Cash --balance 100000
  python3 skills/finance-life/scripts/finance.py expense add --entity Personal --name Rent --amount 20000
  python3 skills/finance-life/scripts/finance.py snapshot
'
python3 skills/thai-personal-tax/scripts/tax.py --employment 600000
```

CI runs the same commands. Green locally is not proof; read the CI run.
