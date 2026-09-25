#!/usr/bin/env python3
"""Validate public discovery pages before publishing; no network or dependencies."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://umay.dev'
errors = []


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.refs = []
        self.ids = []
        self.h1 = 0
        self.canonical = []
        self.descriptions = []
        self.titles = []
        self.capture_title = False
        self.lang = None
        self.anchor_depth = 0
        self.images = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'html':
            self.lang = d.get('lang')
        if tag == 'h1':
            self.h1 += 1
        if tag == 'title':
            self.capture_title = True
        if tag == 'a':
            if self.anchor_depth:
                errors.append(f'{self.path.relative_to(ROOT)}: nested links')
            self.anchor_depth += 1
        if d.get('id'):
            self.ids.append(d['id'])
        if tag == 'link' and d.get('rel') == 'canonical':
            self.canonical.append(d.get('href'))
        if tag == 'meta' and d.get('name') == 'description':
            self.descriptions.append(d.get('content', ''))
        if tag == 'img':
            self.images.append(d)
            for variant in d.get('srcset', '').split(','):
                if variant.strip():
                    self.refs.append(variant.strip().split()[0])
            if not d.get('alt'):
                errors.append(f'{self.path.relative_to(ROOT)}: image missing alt')
        for attr in ['src', 'href']:
            if attr in d:
                self.refs.append(d[attr])

    def handle_endtag(self, tag):
        if tag == 'title':
            self.capture_title = False
        if tag == 'a':
            self.anchor_depth = max(0, self.anchor_depth - 1)

    def handle_data(self, text):
        if self.capture_title:
            self.titles.append(text)


def resolve(ref, source):
    u = urlsplit(ref)
    if u.scheme not in ['', 'https', 'http'] or u.netloc not in ['', 'umay.dev']:
        return None, None
    path = (ROOT / unquote(u.path).lstrip('/') if u.path.startswith('/') else source.parent / unquote(u.path)).resolve() if u.path else source
    if path.is_dir():
        path = path / 'index.html'
    return path, unquote(u.fragment)


sitemap = ET.parse(ROOT / 'sitemap.xml')
urls = [node.text for node in sitemap.findall('.//{*}loc')]
if len(urls) != len(set(urls)):
    errors.append('Duplicate sitemap URLs')
files = []
for url in urls:
    path, _ = resolve(url, ROOT / 'index.html')
    if path is None or not path.is_file():
        errors.append(f'Missing sitemap destination: {url}')
    else:
        files.append(path)
pages = {path: Page(path) for path in files}
titles = []
for path, page in list(pages.items()):
    name = path.relative_to(ROOT)
    expected = BASE + ('/' if name.as_posix() == 'index.html' else '/' + name.as_posix().removesuffix('index.html'))
    if page.canonical != [expected]:
        errors.append(f'{name}: incorrect canonical {page.canonical}')
    if page.h1 != 1:
        errors.append(f'{name}: expected one h1, found {page.h1}')
    if page.lang != 'en':
        errors.append(f'{name}: missing English language declaration')
    if len(page.descriptions) != 1 or not page.descriptions[0].strip():
        errors.append(f'{name}: missing/duplicate meta description')
    if not page.titles:
        errors.append(f'{name}: missing title')
    titles.append(''.join(page.titles))
    if len(page.ids) != len(set(page.ids)):
        errors.append(f'{name}: duplicate element IDs')
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', path.read_text(), re.S):
        try:
            data = json.loads(raw)
            if data.get('@type') in ['SoftwareApplication', 'MobileApplication']:
                for field in ['name', 'operatingSystem', 'applicationCategory', 'offers']:
                    if not data.get(field):
                        errors.append(f'{name}: application schema missing {field}')
        except ValueError as e:
            errors.append(f'{name}: invalid JSON-LD: {e}')
    for ref in page.refs:
        target, fragment = resolve(ref, path)
        if target is None:
            continue
        if not target.is_file():
            errors.append(f'{name}: broken local URL {ref}')
        elif fragment and target.suffix == '.html':
            if target not in pages:
                pages[target] = Page(target)
            if fragment not in pages[target].ids:
                errors.append(f'{name}: missing fragment {ref}')

for title, count in Counter(titles).items():
    if count > 1:
        errors.append(f'Duplicate title: {title}')

products = json.loads((ROOT / 'content/seo/products.json').read_text())
for product in products:
    url = BASE + '/' + product['slug'] + '/'
    if url not in urls:
        errors.append('Product absent from sitemap: ' + url)
    path = ROOT / product['slug'] / 'index.html'
    for img in pages[path].images:
        if not all(img.get(k) for k in ['width', 'height', 'srcset', 'sizes']):
            errors.append(f'{product["slug"]}: image missing responsive dimensions')
home = pages[ROOT / 'index.html']
if len([ref for ref in home.refs if ref.startswith('https://apps.apple.com/')]) != len(products):
    errors.append('Homepage must link directly to the store for every active app')
if 'https://umay.dev/sitemap.xml' not in (ROOT / 'robots.txt').read_text():
    errors.append('robots.txt lacks sitemap declaration')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'PASS: {len(files)} sitemap pages; titles, descriptions, canonicals, JSON-LD, local links, anchors, images and store links.')
