#!/usr/bin/env python3
"""Create a new post from tools/templates/post.html.

Interactive: prompts for the metadata fields, substitutes {{PLACEHOLDERS}},
and writes the result to posts/<slug>.html. Does NOT touch the nav block in
other files — run tools/regenerate_nav.py afterwards.

    python3 tools/new_post.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "tools" / "templates" / "post.html"
POSTS_DIR = ROOT / "posts"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

PROMPTS = [
    ("slug",            "Slug (lowercase, hyphens, e.g. 'lucca' or 'san-francisco')"),
    ("title",            "Title (e.g. 'Inside the Walls')"),
    ("subtitle",         "Subtitle"),
    ("subtitle_short",   "Short title essence for <title> tag (e.g. 'Saudade' or 'Napoleon's island')"),
    ("meta_description", "Meta description (~100–150 chars, one sentence, same voice as the essay)"),
    ("location",         "Location string (e.g. 'Lucca, Tuscany')"),
    ("trip_dates",       "Trip dates (e.g. '25–30 April 2019')"),
    ("trip_end",         "Trip end ISO date (YYYY-MM-DD)"),
    ("country",          "Country (e.g. 'Italy')"),
]


def ask(label: str) -> str:
    while True:
        val = input(f"{label}: ").strip()
        if val:
            return val
        print("  (required)")


def validate(answers: dict[str, str]) -> str | None:
    if not SLUG_RE.match(answers["slug"]):
        return "slug must be lowercase letters/digits with hyphens (no spaces or special chars)"
    if not ISO_DATE_RE.match(answers["trip_end"]):
        return "trip_end must be YYYY-MM-DD"
    return None


def main() -> int:
    if not TEMPLATE_PATH.exists():
        print(f"error: template not found at {TEMPLATE_PATH}", file=sys.stderr)
        return 1

    answers = {key: ask(label) for key, label in PROMPTS}

    err = validate(answers)
    if err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    target = POSTS_DIR / f"{answers['slug']}.html"
    if target.exists():
        print(f"error: {target.relative_to(ROOT)} already exists", file=sys.stderr)
        return 1

    text = TEMPLATE_PATH.read_text(encoding="utf-8")
    for key, value in answers.items():
        text = text.replace("{{" + key.upper() + "}}", value)

    target.write_text(text, encoding="utf-8")
    print(f"\nCreated {target.relative_to(ROOT)}")
    print()
    print("Next step — regenerate the Places dropdown across all pages:")
    print("  python3 tools/regenerate_nav.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
