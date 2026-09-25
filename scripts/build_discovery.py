#!/usr/bin/env python3
"""Build crawlable product discovery pages using only Python's standard library."""
from pathlib import Path
from html import escape, unescape
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://umay.dev'
PRODUCTS = json.loads((ROOT / 'content/seo/products.json').read_text())
GUIDES = json.loads((ROOT / 'content/seo/guides.json').read_text())
E = escape


def write(path, text):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    text = '\n'.join(line.rstrip() for line in text.splitlines()) + '\n'
    if not path.exists() or path.read_text() != text:
        path.write_text(text)


def schema(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2).replace('</', '<\\/') + '\n</script>'


def meta(text, key, value, attr='name'):
    tag = f'<meta {attr}="{key}" content="{E(value, quote=True)}" />'
    pattern = rf'<meta\s+{attr}="{re.escape(key)}"[^>]*>'
    if re.search(pattern, text):
        return re.sub(pattern, lambda _: tag, text)
    return text.replace('</head>', '  ' + tag + '\n</head>')


def page(title, description, url, body, extra=''):
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{E(title)} | umay.dev</title>
  <meta name="description" content="{E(description, quote=True)}" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <link rel="canonical" href="{BASE}{url}" />
  <link rel="icon" href="/assets/favicon.png" />
  <link rel="stylesheet" href="/css/umay.css" />
  <link rel="stylesheet" href="/css/discovery.css" />
  <meta property="og:type" content="{'article' if url.startswith('/guides/') and url != '/guides/' else 'website'}" />
  <meta property="og:site_name" content="umay.dev" />
  <meta property="og:title" content="{E(title, quote=True)}" />
  <meta property="og:description" content="{E(description, quote=True)}" />
  <meta property="og:url" content="{BASE}{url}" />
  <meta property="og:image" content="{BASE}/assets/og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
  {extra}
</head>
<body>
  <nav class="discovery-nav" aria-label="Main navigation"><a href="/">umay.dev</a><a href="/#products">Apps</a><a href="/guides/">Guides</a><a href="/blog/">Product stories</a></nav>
  <main class="editorial">{body}</main>
  <footer class="discovery-nav"><a href="/">All apps by umay.dev</a><a href="mailto:experlercom@gmail.com">Contact &amp; support</a></footer>
</body>
</html>
'''


def store_link(text):
    match = re.search(r'href="(https://apps\.apple\.com/[^" ]+)"', text)
    if not match:
        raise ValueError('Missing App Store link')
    return re.sub(r'apps\.apple\.com/[a-z]{2}/app/', 'apps.apple.com/app/', unescape(match[1]))


def update_product(p):
    path = p['slug'] + '/index.html'
    text = (ROOT / path).read_text()
    p['store'] = store_link(text)
    text = re.sub(r'https://apps\.apple\.com/[a-z]{2}/app/', 'https://apps.apple.com/app/', text)
    text = text.replace('/#projects', '/#products')
    text = text.replace('/fenno/privacy', '/fenno-privacy-policy.html').replace('/fenno/terms', '/fenno-terms-of-use.html')
    if p['slug'] == 'mindtype':
        text = text.replace('/mindtype_privacy_policy.html', p['privacy']).replace('/mindtype_terms_of_use.html', p['terms'])
    text = re.sub(r'<title>.*?</title>', lambda _: '<title>' + E(p['title']) + '</title>', text, flags=re.S)
    for key, value, attr in [('description', p['summary'], 'name'), ('og:title', p['title'], 'property'), ('og:description', p['summary'], 'property'), ('twitter:title', p['title'], 'name'), ('twitter:description', p['summary'], 'name'), ('og:image', BASE + '/' + p['icon'], 'property'), ('twitter:image', BASE + '/' + p['icon'], 'name')]:
        text = meta(text, key, value, attr)
    # This span belongs to the single existing h1, preserving each app's wordmark.
    text = re.sub(r'<span class="product-purpose">.*?</span>', '', text, flags=re.S)
    text = text.replace('</h1>', '<span class="product-purpose">' + E(p['heading']) + '</span></h1>', 1)
    if '/css/discovery.css' not in text:
        text = text.replace('</head>', '  <link rel="stylesheet" href="/css/discovery.css" />\n</head>')

    def update_schema(match):
        obj = json.loads(match[1])
        if obj.get('@type') in ['MobileApplication', 'SoftwareApplication']:
            obj.update({'description': p['summary'], 'applicationCategory': p['category'], 'url': BASE + '/' + p['slug'] + '/', 'downloadUrl': p['store'], 'image': BASE + '/' + p['icon']})
            # Unverified ratings and stale dates must not masquerade as current data.
            obj.pop('aggregateRating', None)
            obj.pop('dateModified', None)
        return schema(obj)

    text = re.sub(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', update_schema, text, flags=re.S)
    guide = next((g for g in GUIDES if g['product'] == p['slug']), None)
    guide_link = f'<p><a href="/guides/{guide["slug"]}/">{E(guide["title"])}</a> — a practical guide to getting started.</p>' if guide else '<p><a href="/guides/">Explore our iPhone and Mac app guides</a>.</p>'
    legal = ' · '.join(f'<a href="{p[key]}">{label}</a>' for key, label in [('privacy', 'Privacy policy'), ('terms', 'Terms of use')] if key in p)
    panel = f'''<!-- discovery:start -->
<section class="discovery-panel" aria-label="Download and useful links">
  <h2>Get started with {E(p['name'])}</h2>
  <p>{E(p['summary'])}</p>
  <p>Check the App Store for supported devices, minimum OS version, availability in your region and current local pricing. Some features may require an in-app purchase.</p>
  <a class="store-link" href="{E(p['store'], quote=True)}">View on {'Mac ' if p['platform'] == 'macOS' else ''}App Store</a>
  {guide_link}
  <p>{legal + ' · ' if legal else ''}<a href="mailto:experlercom@gmail.com">Contact support</a> · <a href="/#products">Explore all apps</a></p>
</section>
<!-- discovery:end -->'''
    if '<!-- discovery:start -->' in text:
        text = re.sub(r'<!-- discovery:start -->.*?<!-- discovery:end -->', lambda _: panel, text, flags=re.S)
    else:
        text = re.sub(r'(<footer\b)', lambda m: panel + '\n' + m[1], text, count=1)
    write(path, text)


def build_guides():
    for g in GUIDES:
        p = next(p for p in PRODUCTS if p['slug'] == g['product'])
        image = f'<figure><img src="/{g["image"]}" alt="{E(g["caption"], quote=True)}" loading="lazy" /><figcaption>{E(g["caption"])}</figcaption></figure>' if 'image' in g else ''
        body = f'''<a href="/guides/">All guides</a>
<h1>{E(g['title'])}</h1><p class="byline">By <a href="/#about">umay.dev</a>, maker of {E(p['name'])}</p>
<p class="lead">{E(g['description'])}</p>{g['body']}{image}
<aside class="discovery-panel"><h2>Try {E(p['name'])}</h2><p>{E(p['summary'])}</p><p><a href="/{p['slug']}/">Explore {E(p['name'])}, features and pricing</a></p><a class="store-link" href="{E(p['store'], quote=True)}">View on App Store</a></aside>'''
        url = f'/guides/{g["slug"]}/'
        data = {'@context': 'https://schema.org', '@type': 'Article', 'headline': g['title'], 'description': g['description'], 'inLanguage': 'en', 'mainEntityOfPage': BASE + url, 'author': {'@type': 'Organization', 'name': 'umay.dev', 'url': BASE + '/#about'}, 'publisher': {'@type': 'Organization', 'name': 'umay.dev', 'url': BASE + '/'}}
        if 'image' in g:
            data['image'] = BASE + '/' + g['image']
        crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Apps', 'item': BASE + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'Guides', 'item': BASE + '/guides/'}, {'@type': 'ListItem', 'position': 3, 'name': g['title'], 'item': BASE + url}]}
        write('guides/' + g['slug'] + '/index.html', page(g['title'], g['description'], url, body, schema(data) + schema(crumbs)))
    cards = ''.join(f'<article><h2><a href="/guides/{g["slug"]}/">{E(g["title"])}</a></h2><p>{E(g["description"])}</p></article>' for g in GUIDES)
    write('guides/index.html', page('Practical Guides for iPhone & Mac Apps', 'Learn to color grade iPhone videos, add captions, keep a mood journal and set up WiFi monitoring on Mac with practical umay.dev app guides.', '/guides/', '<h1>Make more of your apps</h1><p class="lead">Practical workflows for creating videos, keeping a journal and setting up your Mac.</p>' + cards))


def build_blog():
    posts = json.loads((ROOT / 'blog/posts.json').read_text())
    posts.sort(key=lambda p: p['date'], reverse=True)
    cards = ''.join(f'<article><h2><a href="/blog/{p["slug"]}.html">{E(p["title"])}</a></h2><p>{E(p["excerpt"])}</p></article>' for p in posts)
    write('blog/index.html', page('Product Stories & App Development Notes', 'Stories behind the iPhone and Mac apps made by umay.dev, with links to practical guides and product details.', '/blog/', '<h1>Stories behind the apps</h1><p class="lead">Meet the ideas behind our products. For hands-on instructions, visit the <a href="/guides/">app guides</a>.</p>' + cards))
    # Existing stories already contain complete HTML. Use that single source at runtime.
    for post in posts:
        path = ROOT / ('blog/' + post['slug'] + '.html')
        text = path.read_text()
        if 'id="prerendered-content"' in text:
            text = text.replace('id="prerendered-content"', 'class="blog-post-content"')
            text = re.sub(r'<div class="blog-post-content" id="postContent"></div>', '', text)
            text = re.sub(r'<script>\s*fetch\(.*?</script>', '', text, flags=re.S)
            text = re.sub(r'<script>\s*// Hide prerendered content.*?</script>', '', text, flags=re.S)
        text = text.replace('href="/#blog"', 'href="/blog/"')
        write(path, text)


def build_home():
    text = (ROOT / 'index.html').read_text()
    text = re.sub(r'<title>.*?</title>', '<title>umay.dev — Independent Apps for iPhone, iPad &amp; Mac</title>', text)
    text = meta(text, 'description', 'Discover independent iPhone, iPad and Mac apps for video editing, mood journaling, personal productivity and home automation. Explore features and download.')
    text = meta(text, 'og:title', 'umay.dev — Independent Apps for iPhone, iPad & Mac', 'property')
    text = meta(text, 'og:description', 'Explore apps for video editing, journaling, productivity and home automation, with practical guides to get started.', 'property')
    text = meta(text, 'twitter:title', 'umay.dev — Independent Apps for iPhone, iPad & Mac')
    text = meta(text, 'twitter:description', 'Explore apps for video editing, journaling, productivity and home automation, with practical guides to get started.')
    text = text.replace('We build apps<br/>people love.', 'Find your next<br/>favorite app.')
    text = re.sub(r'(<p class="hero-tagline">).*?</p>', lambda m: m[1] + '\n          Edit videos, keep a personal journal, explore your decision-making habits or automate your home. Discover independent apps for <strong>iPhone, iPad and Mac</strong>, made by <strong>umay.dev</strong>.\n        </p>', text, count=1, flags=re.S)
    text = text.replace('6+</div>', '9</div>')
    text = text.replace('<a href="#blog">blog</a>', '<a href="/guides/">guides</a><a href="/blog/">blog</a>')
    if '/css/discovery.css' not in text:
        text = text.replace('</head>', '<link rel="stylesheet" href="/css/discovery.css" />\n</head>')
    # Render every card from the catalogue; gallery contents survive every rebuild.
    for asset in ['css/discovery.css', 'js/umay.js']:
        version = hashlib.sha256((ROOT / asset).read_bytes()).hexdigest()[:12]
        text = re.sub(r'(["\'])/?' + re.escape(asset) + r'(?:\?[^"\']*)?(["\'])',
                      lambda m: m[1] + '/' + asset + '?v=' + version + m[2], text)
    def card(p):
        slug, name = p['slug'], E(p['name'])
        screenshots = ''.join(f'<img src="/{shot["src"]}" alt="{E(shot["alt"], quote=True)}" loading="lazy" />' for shot in p['screenshots'])
        wide = ' gallery-wide' if p['platform'] == 'macOS' else ''
        return f'''<article class="project-card project-featured" data-color="{p['color']}" aria-labelledby="app-{slug}">
  <div class="project-icon"><img src="/{p['icon']}" alt="{name} app icon" loading="lazy" /></div>
  <div class="project-info">
    <h3 id="app-{slug}"><a href="/{slug}/">{name}</a></h3>
    <div class="project-tags"><span>{p['platform']}</span></div>
    <p>{E(p['summary'])}</p>
  </div>
  <div class="project-actions">
    <a class="store-link" href="{E(p['store'], quote=True)}" aria-label="Download {name} on the App Store">Download for {'Mac' if p['platform'] == 'macOS' else 'iOS'} <span aria-hidden="true">↗</span></a>
    <a class="details-link" href="/{slug}/">Explore {name} <span aria-hidden="true">→</span></a>
  </div>
  <div class="project-gallery{wide}">
    <div class="gallery-toolbar"><span>{len(p['screenshots'])} screenshots <span class="gallery-hint">· Scroll to explore</span></span>
      <div class="gallery-controls" hidden><button type="button" data-direction="-1" aria-controls="gallery-{slug}" aria-label="Previous {name} screenshots">←</button><button type="button" data-direction="1" aria-controls="gallery-{slug}" aria-label="Next {name} screenshots">→</button></div>
    </div>
    <div class="project-preview" id="gallery-{slug}" tabindex="0" role="region" aria-label="{name} screenshots">{screenshots}</div>
  </div>
</article>'''
    cards_html = '\n'.join(card(p) for p in PRODUCTS)
    text = re.sub(r'(<div class="projects-grid">).*?(</section>)', lambda m: m[1] + '\n' + cards_html + '\n</div>\n</div>\n' + m[2], text, count=1, flags=re.S)
    cards = ''.join(f'<a href="/guides/{g["slug"]}/" class="blog-card"><div class="blog-card-title">{E(g["title"])}</div><div class="blog-card-excerpt">{E(g["description"])}</div></a>' for g in GUIDES)
    block = '<!-- guides:start -->\n<div class="blog-grid">' + cards + '</div>\n<!-- guides:end -->'
    if '<!-- guides:start -->' in text:
        text = re.sub(r'<!-- guides:start -->.*?<!-- guides:end -->', lambda _: block, text, flags=re.S)
    else:
        text = re.sub(r'<div id="blogPosts" class="blog-grid">.*?</div>', lambda _: block, text, flags=re.S)
    text = text.replace('Thoughts &amp; updates', 'Practical guides for your apps').replace('From the Blog', 'Get Started')
    text = re.sub(r'<p class="blog-empty"[^>]*>.*?</p>', '', text)
    text = re.sub(r'<p style="margin-top:32px;.*?</p>', '<p style="margin-top:32px;text-align:center;"><a href="/guides/">All app guides</a> · <a href="/blog/">Stories behind the apps</a></p>', text, flags=re.S)
    write('index.html', text)


def sitemap(today):
    paths = ['index.html', 'blog/index.html', *[p['slug'] + '/index.html' for p in PRODUCTS]]
    paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'guides').rglob('*.html'))]
    paths += ['blog/' + p['slug'] + '.html' for p in json.loads((ROOT / 'blog/posts.json').read_text())]
    # Preserve the independently accessible older product pages as well.
    paths += [p.name for p in ROOT.glob('*.html') if p.stem in ['arithmio', 'calendart', 'filmzy', 'jeoatlas', 'kidity', 'moodconnect', 'nazar']]
    state_path = ROOT / 'content/seo/page-state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    tree = ET.Element('{' + ns + '}urlset')
    next_state = {}
    for path in sorted(set(paths)):
        content = (ROOT / path).read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        old = state.get(path, {})
        lastmod = old.get('lastmod') if old.get('sha256') == digest else today
        next_state[path] = {'sha256': digest, 'lastmod': lastmod}
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', content.decode())
        if not canonical:
            raise ValueError('Missing canonical: ' + path)
        node = ET.SubElement(tree, '{' + ns + '}url')
        ET.SubElement(node, '{' + ns + '}loc').text = canonical[1]
        ET.SubElement(node, '{' + ns + '}lastmod').text = lastmod
    ET.indent(tree, space='  ')
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(tree, encoding='unicode') + '\n')
    write(state_path, json.dumps(next_state, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=datetime.date.today().isoformat(), help='Actual publication/update date (YYYY-MM-DD)')
    parser.add_argument('--sitemap-only', action='store_true')
    args = parser.parse_args()
    datetime.date.fromisoformat(args.date)
    if not args.sitemap_only:
        for product in PRODUCTS:
            update_product(product)
        build_guides()
        build_blog()
        build_home()
        subprocess.run([sys.executable, str(ROOT / 'scripts/optimize_images.py')], check=True)
    sitemap(args.date)
    print('Discovery pages and sitemap are up to date.')
