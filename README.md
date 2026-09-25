# umay.dev

Static product website for an independent app studio. The primary audience is global and the marketing pages are in English. The site uses plain HTML, CSS and JavaScript; no application server or client-side framework is required.

## Content and publishing

- Active product pages: `<product>/index.html`.
- Product search titles, descriptions, categories and related guides: `content/seo/products.json`.
- Practical guides: `content/seo/guides.json`. Their HTML pages under `guides/` are generated.
- Product stories: `blog/*.html`; the blog catalogue is `blog/posts.json`. Existing `.md` files are historical source material, not fetched by the published pages. Edit the HTML story when updating it.
- The home page includes static product links, direct store links and guide links. All essential content is available without JavaScript.

After editing content, run from the repository root with Python 3.12+ and the `cwebp` command installed:

```sh
python3 scripts/build_discovery.py
python3 scripts/check_site.py
git diff --check
```

On macOS, `cwebp` is supplied by Homebrew's `webp` package. The build creates responsive WebP files, updates product metadata and guide/blog indexes, and regenerates `sitemap.xml`. The original PNGs are preserved. Commit the generated pages, image derivatives, manifest and sitemap with the source changes using your normal publishing process.

`content/seo/page-state.json` records each page's final content hash and modification date. An unchanged page retains its existing `lastmod`; do not change every date simply because a deployment ran. To supply the actual publication date explicitly, use `--date YYYY-MM-DD`. For a sitemap-only refresh after editing an existing static page, run `python3 scripts/build_discovery.py --sitemap-only`.

When adding an app:

1. Create its landing page with its real features, privacy links and App Store URL.
2. Add a record to `content/seo/products.json`, including `color` and the complete `screenshots` list (source path and alt text). The build generates the home card, gallery and separate detail/store links.
3. Add a genuinely useful guide if applicable, then run the build and checks above.
4. Keep prices, platform requirements and any ratings consistent with verifiable product information. Do not add unverified ratings or guarantees.

The checker validates the sitemap's local destinations, unique titles, descriptions, canonical URLs, one H1 per page, JSON-LD syntax, local links/fragments, responsive product images and direct home-page store links. It does not claim to validate Google's rich-result eligibility or external store availability.

## Preview

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/`. Check the homepage, a product and a guide at mobile and desktop widths. Existing analytics integrations have not been extended by this SEO update.

## Credits

The repository originally used the Start Bootstrap Landing Page template (MIT). See `LICENSE`. Original photography credit: Marvin Meyer on Unsplash.
