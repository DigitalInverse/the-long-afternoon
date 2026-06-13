# Map generation prompt for Claude Code

Each new post needs an inline SVG map in `<div class="map-wrap">`,
matching the style of existing posts. The `tools/templates/post.html`
template leaves a `<div class="map-placeholder">...</div>` to be
replaced by a real map.

This is a manual step after creating a new post with `new_post.py`.
Map generation is not automated because each map needs region-specific
judgment (which cities to highlight, where to place sea labels, etc.).

## Usage

1. Create the new post with `tools/new_post.py`
2. Open Claude Code in this repo
3. Paste the prompt below, replacing `posts/X.html` with the actual path

## Prompt

​```
Generate an inline SVG map for posts/X.html, replacing the existing
<div class="map-placeholder">...</div>. Use the maps in
posts/liguria.html, posts/sardinia.html, posts/sicily.html,
posts/elba.html, posts/lucca.html, and posts/kefalonia.html as
templates for style, structure, and conventions.

CONTEXT
Each existing post has a <div class="map-wrap"> containing an inline
SVG of the region the post is about — coastline paths, city dots,
SVG text labels for cities, region name, sub-region, stat numbers
(population, area), and sea/ocean labels. The viewBox is 0 0 680 310.

PROCEDURE
1. Read posts/liguria.html (or another existing post) to understand
   the exact SVG structure, styling, fonts, colours, and label
   classes: mtitle, mtitle-sub, mstat-num, mstat-label, mcity-label,
   mcity-label-highlight, msea-label, mcoast, mcity-dot.
2. Source coastline/border data from OpenStreetMap. For country or
   state outlines, use admin_level=2 (country) or admin_level=4
   (state) boundary.
3. Simplify geometry to keep SVG file size reasonable (~5000 path
   characters max). Use shapely's simplify() with a tolerance that
   preserves recognisable shape.
4. Project coordinates to fit the 0 0 680 310 viewBox while
   preserving aspect ratio. Centre the region with ~30 units margin.
5. Add 3-6 city dots and labels. Highlight the post's main city with
   the orange-red accent (#b85a38) and the .mcity-label-highlight
   class. Other cities use the standard .mcity-label.
6. Add stats: population and area of the region/country, formatted
   the same as existing maps.
7. Add sea/ocean labels in italics where appropriate. Use the
   .msea-label class.
8. Add a title (e.g., "Portugal", "New South Wales") and sub-label
   (e.g., "WESTERN EUROPE", "SOUTHEAST AUSTRALIA") in the same
   position and style as other maps.
9. Replace only the <div class="map-placeholder">...</div> inside
   <div class="map-wrap">. Don't change anything else.
10. Show me the result before committing.

DO NOT
- Change anything outside <div class="map-wrap">
- Change the viewBox dimensions (must stay 0 0 680 310)
- Add features not present in existing maps (legends, scale bars, etc.)
- Commit (leave changes staged for review)
​```

## Special cases

### Perth

Perth, Fremantle and Rottnest Island are geographically so close
together that on a full Western Australia map they collapse into a
single cluster of overlapping dots. Use an inset, or zoom the main
map to just the southwest corner of WA.
