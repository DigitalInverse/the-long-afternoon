# tools/

Two small scripts that keep the Places dropdown consistent across every HTML
file. Pure Python 3, stdlib only.

## Adding a new post

```sh
python3 tools/new_post.py
python3 tools/regenerate_nav.py
```

`new_post.py` prompts for:

| Field        | Example                  | Used in                                                  |
|--------------|--------------------------|----------------------------------------------------------|
| `slug`       | `lucca`, `san-francisco` | Filename `posts/<slug>.html`, image dir, dropdown label  |
| `title`      | `Inside the Walls`       | `<title>` and `<h1 class="hero-title">`                  |
| `subtitle`   | `A week in Puccini's…`   | `<p class="hero-subtitle">`                              |
| `location`   | `Lucca, Tuscany`         | First half of `<p class="hero-meta">`                    |
| `trip_dates` | `25–30 April 2019`       | Second half of `<p class="hero-meta">`                   |
| `trip_end`   | `2019-04-30`             | `data-trip-end` (drives dropdown ordering within country)|
| `country`    | `Italy`                  | `data-country` (drives dropdown grouping)                |

The script copies `tools/templates/post.html`, substitutes `{{PLACEHOLDERS}}`,
and writes `posts/<slug>.html`. It does **not** touch other files — run
`regenerate_nav.py` to update the dropdown everywhere.

## Editing or deleting a post

Edit metadata (`data-country`, `data-trip-end`, title) directly in the post,
or delete the file. Then run `tools/regenerate_nav.py` to propagate.

## How regenerate_nav.py works

1. Scans `posts/*.html` and reads `data-trip-end` and `data-country` from each
   `<article>` tag.
2. Groups posts by country (alphabetical). Countries with one post become a
   `country-group single` (direct link); countries with two or more become a
   `country-group multi` (submenu).
3. Within a country, posts are sorted by `data-trip-end` descending (most
   recent trip first).
4. Dropdown link text is derived from the slug: `san-francisco` → `San
   Francisco`. The `<h1>` title is intentionally not used.
5. Replaces the content between `<!-- NAV:START -->` and `<!-- NAV:END -->` in
   every HTML file. Paths are adjusted automatically for files in `/` vs
   `/posts/`.

The script is idempotent — running it on an unchanged tree produces zero
changes.

## Files

```
tools/
├── README.md
├── new_post.py
├── regenerate_nav.py
└── templates/
    └── post.html
```

## Required markers and attributes

Every HTML file must contain `<!-- NAV:START -->` and `<!-- NAV:END -->`
around its nav block. Every post must contain `data-trip-end="YYYY-MM-DD"`
and `data-country="..."` on its `<article>` tag. The template already
includes both; posts missing either are skipped with a warning.
