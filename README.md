# Baritone Bedrock â€” website

The website of [Baritone Bedrock](https://github.com/miked06/baritone-bedrock), the Baritone pathfinding bot ported to Minecraft Bedrock for Windows.

**Live:** https://miked06.github.io/baritone-bedrock-website/

## What's inside

A static site (plain HTML, CSS and JavaScript, no build step), served by GitHub Pages.

| Path | |
|---|---|
| `index.html` | The page |
| `assets/css/style.css` | Styles (dark theme in Baritone's render colors, responsive, `prefers-reduced-motion` aware) |
| `assets/js/hero.js` | The hero scene: an isometric voxel world where a bot runs A*, shows its path and walks to the goal |
| `assets/js/pathfinder.js` | The interactive pathfinder demo (A* with Baritone's costs in ticks) |
| `assets/js/main.js` | Scroll reveals, counters, the Minecraft chat demo, the gallery and lightbox |
| `assets/js/media.js` | The gallery list |
| `media/` | Gameplay videos and screenshots |

## Run it locally

Any static server works:

```bash
python -m http.server 8000
```

then open http://localhost:8000.

## Publishing

GitHub Pages serves the `main` branch from the repository root (*Settings â†’ Pages â†’ Deploy from a branch â†’ `main` / `/ (root)`*). `.nojekyll` disables Jekyll processing.

## Adding gameplay media

Put the file in `media/` (H.264 MP4 at 1280Ã—720 without audio, or JPEG), then add an entry to `assets/js/media.js`:

```js
{ type: "video", src: "media/clip.mp4", poster: "media/clip.jpg", title: "Title", cmd: "#goto ...", text: "caption" }
```

Not affiliated with Mojang Studios or Microsoft. "Minecraft" is a trademark of Mojang Synergies AB.

## Search and release maintenance

The site uses static HTML for the homepage and download, command and schematic guides.
Run `python scripts/check_site.py` before publishing. Update visible version/package
facts and SoftwareApplication JSON-LD together when a release changes. Sitemap
last-modified dates should change only when page content materially changes.

Canonical URLs use the corrected repository name, `baritone-bedrock-website`.
The old misspelling is not an alternate site URL. `404.html` is marked noindex.
The gallery labels its older footage; videos load on demand to limit network work.

Verify the live URL-prefix property in Google Search Console and submit
`https://miked06.github.io/baritone-bedrock-website/sitemap.xml`. Ownership verification
and requesting indexing require the owner's Search Console account; this repository
cannot verify ownership or guarantee indexing. GitHub Pages project-level robots.txt
is informative only: crawlers read the origin's `/robots.txt`, outside this repository's
subpath. The default absence of an origin robots file does not block crawling.

Google's [AI features guidance](https://developers.google.com/search/docs/appearance/ai-features)
says AI Overviews and AI Mode use normal SEO foundations: indexable content, useful
text, internal links and accurate structured data. There is no required AI schema,
llms.txt file or guaranteed inclusion. This site does not add fake reviews, hidden
keyword text or unsupported FAQ rich-result claims.
