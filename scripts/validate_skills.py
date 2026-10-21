#!/usr/bin/env python3
"""Validate every skill in this repo against the Agent Skills minimum.

Checks: SKILL.md exists, YAML frontmatter parses, name matches the directory,
name and description are present, description is under 1024 chars, and every
referenced file (references/, scripts/, templates/) exists.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("unterminated frontmatter")
    block = text[4:end]
    data: dict = {}
    current_key = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith(("  ", "\t")) and current_key:
            continue  # nested list/map under a known key
        key, _, value = raw.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        data[key] = value
        current_key = key
    return data


def check_links(skill_dir: Path, text: str) -> list[str]:
    problems = []
    for rel in re.findall(r"`((?:references|scripts|templates|assets)/[^`]+)`", text):
        if not (skill_dir / rel).exists():
            problems.append(f"{skill_dir.name}: referenced file missing: {rel}")
    return problems


def main() -> int:
    problems: list[str] = []
    dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    if not dirs:
        print("no skills found")
        return 1
    for skill in dirs:
        md = skill / "SKILL.md"
        if not md.exists():
            problems.append(f"{skill.name}: no SKILL.md")
            continue
        text = md.read_text(encoding="utf-8")
        try:
            fm = frontmatter(text)
        except ValueError as exc:
            problems.append(f"{skill.name}: {exc}")
            continue
        name = fm.get("name", "")
        description = fm.get("description", "")
        if not name:
            problems.append(f"{skill.name}: missing name")
        elif not NAME_RE.match(name):
            problems.append(f"{skill.name}: name must be lowercase-hyphenated, got {name!r}")
        elif name != skill.name:
            problems.append(f"{skill.name}: name {name!r} must match the directory")
        if not description:
            problems.append(f"{skill.name}: missing description")
        elif len(description) > 1024:
            problems.append(f"{skill.name}: description over 1024 chars")
        problems.extend(check_links(skill, text))

    if problems:
        print("\n".join(problems))
        return 1
    print(f"ok: {len(dirs)} skills valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
