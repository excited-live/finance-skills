# Finance Skills

Open Agent Skills for documenting a whole financial life in one place: a day job,
side projects and businesses, in a single local file, with runway you can actually act on.

Free, MIT, local-first. Your numbers stay in a file you own.

[![skills.sh](https://skills.sh/b/excited-live/finance-skills)](https://skills.sh/excited-live/finance-skills)

## Install

Any agent that supports the [Agent Skills](https://agentskills.io) format:

```bash
npx skills add excited-live/finance-skills
```

Claude Code, Codex, Antigravity, OpenCode and others read the same `SKILL.md`. If your
agent only takes a directory, clone and point it at `skills/`:

```bash
git clone https://github.com/excited-live/finance-skills.git
```

## Skills

| Skill | What it does |
| --- | --- |
| [`finance-life`](skills/finance-life/SKILL.md) | Builds `~/finance/book.json`: entities, cash, incomes, expenses, debt. Computes per-entity and combined runway. Exports an import bundle. |
| [`thai-personal-tax`](skills/thai-personal-tax/SKILL.md) | Estimates Thai personal income tax for the year with real brackets and deductions. |

## The book

Everything is one JSON file, written by a stdlib-only Python script, no account and no
network. Format and mapping to excited.live: [`skills/finance-life/references/book-format.md`](skills/finance-life/references/book-format.md).

```bash
python3 skills/finance-life/scripts/finance.py init
python3 skills/finance-life/scripts/finance.py entity add --name Personal --type personal --buffer 6
python3 skills/finance-life/scripts/finance.py cash set --entity Personal --name KBank --balance 120000
python3 skills/finance-life/scripts/finance.py snapshot
```

## Privacy

The skills never upload, email or post anything. `export` writes a second file next to
the book and prints the path. Whether that file goes anywhere is the user's decision,
made once, at the end of a session, with the offer spelled out.
