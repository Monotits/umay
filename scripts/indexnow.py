#!/usr/bin/env python3
"""Notify Bing, Yandex and other IndexNow engines about changed pages. Run AFTER the site is deployed.

Usage:
  python3 scripts/indexnow.py            # pages whose sitemap lastmod is today
  python3 scripts/indexnow.py --since 2026-09-01
  python3 scripts/indexnow.py --all
"""
from pathlib import Path
import argparse
import datetime
import json
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
KEY = json.loads((ROOT / 'content/seo/site.json').read_text())['indexNowKey']

parser = argparse.ArgumentParser()
parser.add_argument('--since', default=datetime.date.today().isoformat())
parser.add_argument('--all', action='store_true')
args = parser.parse_args()

ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls = [u.findtext('s:loc', namespaces=ns) for u in ET.parse(ROOT / 'sitemap.xml').findall('s:url', ns)
        if args.all or u.findtext('s:lastmod', namespaces=ns) >= args.since]
if not urls:
    raise SystemExit('No changed URLs to submit.')
body = json.dumps({'host': 'umay.dev', 'key': KEY, 'keyLocation': f'https://umay.dev/{KEY}.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
with urllib.request.urlopen(req, timeout=30) as res:
    print(f'IndexNow: HTTP {res.status}, {len(urls)} URLs submitted.')
