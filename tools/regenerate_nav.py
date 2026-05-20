#!/usr/bin/env python3
"""Regenerate the <!-- NAV:START -->...<!-- NAV:END --> block in every HTML
file from post metadata (data-trip-end, data-country).

Run from anywhere; paths resolve relative to the repo root.

    python3 tools/regenerate_nav.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
ROOT_HTML = [ROOT / "index.html", ROOT / "about.html"]

TITLE_RE = re.compile(r'<h1 class="hero-title">(.*?)</h1>', re.S)
TRIP_END_RE = re.compile(r'data-trip-end="(\d{4}-\d{2}-\d{2})"')
COUNTRY_RE = re.compile(r'data-country="([^"]+)"')
NAV_RE = re.compile(r'(<!-- NAV:START -->)(.*?)(<!-- NAV:END -->)', re.S)


def slug_to_label(slug: str) -> str:
    """Dropdown link text: 'san-francisco' -> 'San Francisco'."""
    return slug.replace("-", " ").title()


def load_posts():
    posts = []
    for path in sorted(POSTS_DIR.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        end = TRIP_END_RE.search(text)
        country = COUNTRY_RE.search(text)
        if not (end and country):
            print(
                f"warning: {path.name} missing data-trip-end or data-country, "
                "skipping",
                file=sys.stderr,
            )
            continue
        title_m = TITLE_RE.search(text)
        posts.append({
            "slug": path.stem,
            "title": title_m.group(1).strip() if title_m else slug_to_label(path.stem),
            "trip_end": end.group(1),
            "country": country.group(1),
        })
    return posts


def group_by_country(posts):
    grouped: dict[str, list] = {}
    for p in posts:
        grouped.setdefault(p["country"], []).append(p)
    for country in grouped:
        grouped[country].sort(key=lambda p: p["trip_end"], reverse=True)
    return grouped


def build_nav(posts, target_is_root: bool) -> str:
    """Return the full nav block as a string (div + nav + ul, no NAV markers)."""
    def post_href(slug: str) -> str:
        return f"posts/{slug}.html" if target_is_root else f"{slug}.html"

    def root_href(name: str) -> str:
        return name if target_is_root else f"../{name}"

    lines = [
        '<div class="site-nav-wrap">',
        '<nav class="site-nav" aria-label="Main">',
        f'  <a href="{root_href("index.html")}" class="site-logo">The Long Afternoon</a>',
        '  <button class="nav-toggle" aria-label="Menu" aria-expanded="false" aria-controls="primary-nav">',
        '    <span></span><span></span><span></span>',
        '  </button>',
        '  <ul class="site-nav-links" id="primary-nav">',
        f'    <li><a href="{root_href("index.html")}">Home</a></li>',
        '    <li class="has-dropdown">',
        '      <button type="button" aria-haspopup="true" aria-expanded="false">Places</button>',
        '      <ul class="nav-dropdown places-menu">',
    ]

    grouped = group_by_country(posts)
    for country in sorted(grouped):
        country_posts = grouped[country]
        if len(country_posts) == 1:
            slug = country_posts[0]["slug"]
            href = post_href(slug)
            label = slug_to_label(slug)
            lines += [
                '        <li class="country-group single">',
                f'          <a href="{href}" class="country-label">{country}</a>',
                '          <ul class="country-submenu">',
                f'            <li><a href="{href}">{label}</a></li>',
                '          </ul>',
                '        </li>',
            ]
        else:
            lines += [
                '        <li class="country-group multi">',
                f'          <span class="country-label">{country}</span>',
                '          <ul class="country-submenu">',
            ]
            for p in country_posts:
                href = post_href(p["slug"])
                label = slug_to_label(p["slug"])
                lines.append(f'            <li><a href="{href}">{label}</a></li>')
            lines += [
                '          </ul>',
                '        </li>',
            ]

    lines += [
        '      </ul>',
        '    </li>',
        f'    <li><a href="{root_href("about.html")}">About</a></li>',
        '  </ul>',
        '</nav>',
        '</div>',
    ]
    return "\n".join(lines)


def update_file(path: Path, nav_html: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if not NAV_RE.search(text):
        print(
            f"warning: {path.relative_to(ROOT)} has no NAV:START/NAV:END markers, skipping",
            file=sys.stderr,
        )
        return False
    new_text = NAV_RE.sub(
        lambda m: f"<!-- NAV:START -->\n{nav_html}\n<!-- NAV:END -->",
        text,
        count=1,
    )
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    posts = load_posts()
    if not posts:
        print("error: no posts found in posts/", file=sys.stderr)
        return 1

    root_nav = build_nav(posts, target_is_root=True)
    post_nav = build_nav(posts, target_is_root=False)

    targets: list[tuple[Path, str]] = [(p, root_nav) for p in ROOT_HTML]
    targets += [(p, post_nav) for p in sorted(POSTS_DIR.glob("*.html"))]

    updated = []
    for path, nav in targets:
        if update_file(path, nav):
            updated.append(path.relative_to(ROOT))

    print(f"Scanned {len(targets)} file(s); {len(updated)} updated.")
    for name in updated:
        print(f"  updated: {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
