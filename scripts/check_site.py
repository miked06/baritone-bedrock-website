"""Dependency-free checks of published pages, metadata and crawlable links."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://miked06.github.io/baritone-bedrock-website/'
RELEASE = json.loads((ROOT / 'release.json').read_text(encoding='utf-8'))


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags, self.jsons = [], []
        self.json = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.json = ''

    def handle_data(self, data):
        if self.json is not None:
            self.json += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.json is not None:
            self.jsons.append(json.loads(self.json))
            self.json = None


pages = {p.name: Page(p.read_text(encoding='utf-8')) for p in ROOT.glob('*.html')}
canonicals = set()
for name, page in pages.items():
    assert sum(t == 'h1' for t, a in page.tags) == 1, name
    assert sum(t == 'title' for t, a in page.tags) == 1, name
    ids = [a['id'] for t, a in page.tags if 'id' in a]
    assert len(ids) == len(set(ids)), f'Duplicate ID in {name}'
    metas = [a for t, a in page.tags if t == 'meta']
    if name == '404.html':
        assert any(a.get('name') == 'robots' and 'noindex' in a.get('content', '') for a in metas)
    else:
        canonical = [a['href'] for t, a in page.tags if t == 'link' and a.get('rel') == 'canonical']
        assert canonical == [BASE + ('' if name == 'index.html' else name)], name
        assert canonical[0] not in canonicals
        canonicals.add(canonical[0])
        assert any(a.get('name') == 'description' and len(a.get('content', '')) > 50 for a in metas), name
        assert any(a.get('property') == 'og:url' and a.get('content') == canonical[0] for a in metas)
        assert page.jsons, f'Missing structured data: {name}'
        source = (ROOT / name).read_text(encoding='utf-8')
        assert RELEASE['version'] in source, f'{name}: missing current version'
        schemas = [node for data in page.jsons for node in data.get('@graph', [data])]
        assert any(node.get('@type') == 'WebPage' and node.get('dateModified') == RELEASE['published']
                   for node in schemas), f'{name}: stale page metadata'
        for tag, attrs in page.tags:
            href = attrs.get('href', '')
            if '/releases/download/' in href:
                assert f"/releases/download/v{RELEASE['version']}/" in href, f'{name}: stale binary link'
        if name in ('index.html', 'download.html'):
            assert RELEASE['windowsPackage'] in source, f'{name}: missing exact package'
            assert RELEASE['minecraftVersion'] in source, f'{name}: missing game version'
            for binary in ('BaritoneBedrock.dll', 'BaritoneControlPanel.exe'):
                assert any(a.get('href', '').endswith(f"/v{RELEASE['version']}/{binary}")
                           for t, a in page.tags if t == 'a'), f'{name}: missing {binary}'
    for data in page.jsons:
        for node in data.get('@graph', [data]):
            if node.get('@type') == 'SoftwareApplication':
                assert node['softwareVersion'] == RELEASE['version']
                assert RELEASE['windowsPackage'] in node['softwareRequirements']
                assert node['releaseNotes'] == RELEASE['releaseUrl']
                assert node['downloadUrl'].endswith(f"/v{RELEASE['version']}/BaritoneBedrock.dll")
    for tag, attrs in page.tags:
        for key in ['href', 'src', 'poster']:
            value = attrs.get(key, '')
            url = urlsplit(value)
            if not value or url.scheme or url.netloc:
                continue
            path = unquote(url.path)
            if path.startswith('/baritone-bedrock-website/'):
                path = path.removeprefix('/baritone-bedrock-website/')
            target = ROOT / (path or name)
            if target.is_dir():
                target /= 'index.html'
            assert target.is_file(), f'{name}: missing {value}'
            if url.fragment and target.suffix == '.html':
                target_page = pages[target.name]
                assert any(a.get('id') == url.fragment for t, a in target_page.tags), f'{name}: broken {value}'

tree = ET.parse(ROOT / 'sitemap.xml')
locations = {e.text for e in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
assert locations == canonicals, 'Sitemap and canonical pages differ'
assert all(e.text == RELEASE['published'] for e in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')), 'Stale sitemap dates'
assert f'Sitemap: {BASE}sitemap.xml' in (ROOT / 'robots.txt').read_text(encoding='utf-8')
assert 'bartione-bedrock-website' not in (ROOT / 'index.html').read_text(encoding='utf-8')
print(f"PASS: {len(pages)} pages, release {RELEASE['version']}, metadata, JSON-LD, internal links, anchors and sitemap")
