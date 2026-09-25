#!/usr/bin/env python3
"""Create responsive WebP derivatives. Original images remain untouched.

Requires Google's cwebp command (brew install webp on macOS).
"""
from concurrent.futures import ThreadPoolExecutor
from html import escape, unescape
from pathlib import Path
import hashlib
import json
import re
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = json.loads((ROOT / 'content/seo/products.json').read_text())
PAGES = [ROOT / 'index.html'] + [ROOT / p['slug'] / 'index.html' for p in PRODUCTS] + sorted((ROOT / 'guides').rglob('*.html'))
PAGES += [ROOT / (name + '.html') for name in ['arithmio', 'calendart', 'filmzy', 'jeoatlas', 'kidity', 'moodconnect', 'nazar']]
OUT = ROOT / 'assets/optimized'
OUT.mkdir(parents=True, exist_ok=True)
MANIFEST = OUT / 'manifest.json'
manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
sources = set()


def source_path(page, src):
    if src.startswith(('https:', 'http:', 'data:')):
        return None
    path = ROOT / src.lstrip('/') if src.startswith('/') else page.parent / src
    return path.resolve()


def attributes(tag):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', tag))


for page in PAGES:
    for tag in re.findall(r'<img\b[^>]*>', page.read_text()):
        src = attributes(tag).get('src', '')
        path = source_path(page, src)
        if path and path.suffix.lower() == '.png' and path.exists():
            sources.add(path)


def convert(path):
    rel = path.relative_to(ROOT).as_posix()
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    old = manifest.get(rel)
    if old and old['sha256'] == digest and all((ROOT / p['path'].lstrip('/')).exists() for p in old['variants']):
        return rel, old
    if content[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Not a PNG: ' + rel)
    width, height = struct.unpack('>II', content[16:24])
    widths = sorted(set(min(width, w) for w in (320, 640, 960)))
    variants = []
    for w in widths:
        h = max(1, round(height * w / width))
        # Include source path and content so browser caches are safe after replacement.
        name = re.sub(r'[^a-z0-9-]', '-', path.stem.lower()) + '-' + hashlib.sha256((rel + digest).encode()).hexdigest()[:12] + '-' + str(w) + '.webp'
        output = OUT / name
        subprocess.run(['cwebp', '-quiet', '-q', '82', '-m', '5', '-resize', str(w), str(h), str(path), '-o', str(output)], check=True)
        variants.append({'width': w, 'height': h, 'path': '/' + output.relative_to(ROOT).as_posix(), 'bytes': output.stat().st_size})
    return rel, {'sha256': digest, 'originalBytes': len(content), 'variants': variants}


if not shutil.which('cwebp'):
    raise SystemExit('cwebp is required; install the WebP tools before running this script.')
with ThreadPoolExecutor(max_workers=4) as pool:
    for rel, record in pool.map(convert, sorted(sources)):
        manifest[rel] = record

for page in PAGES:
    def replace(match):
        tag = match[0]
        attrs = attributes(tag)
        src = attrs.get('src', '')
        path = source_path(page, src)
        if not path or path.suffix.lower() != '.png' or not path.exists():
            return tag
        info = manifest[path.relative_to(ROOT).as_posix()]
        variants = info['variants']
        default = next((v for v in variants if v['width'] >= (320 if page == ROOT / 'index.html' else 640)), variants[-1])
        attrs['src'] = default['path']
        attrs['srcset'] = ', '.join(f'{v["path"]} {v["width"]}w' for v in variants)
        is_icon = 'icon' in attrs.get('class', '').lower() or 'icon' in attrs.get('alt', '').lower() or path.parent.name == 'img'
        if page == ROOT / 'index.html':
            attrs['sizes'] = '64px' if is_icon else '130px'
        else:
            attrs['sizes'] = '120px' if is_icon else '(max-width: 600px) 220px, 320px'
        width = int(attrs.get('width', default['width']))
        attrs['width'] = str(width)
        attrs['height'] = str(round(default['height'] * width / default['width']))
        attrs['decoding'] = 'async'
        if page == ROOT / 'index.html' or not is_icon:
            attrs['loading'] = 'lazy'
        return '<img ' + ' '.join(f'{k}="{escape(unescape(v), quote=True)}"' for k, v in attrs.items()) + ' />'
    original = page.read_text()
    updated = re.sub(r'<img\b[^>]*>', replace, original)
    if updated != original:
        page.write_text(updated)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
print(f'Optimized {len(manifest)} source images; original files preserved.')
