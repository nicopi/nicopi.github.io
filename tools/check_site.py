#!/usr/bin/env python3
"""Check the static site's content, metadata and local references (stdlib only)."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

PAGES = ('index.html', 'biography.html', 'publications.html', 'talks.html', 'patents.html')
ORIGIN = 'https://www.nicolapiovesan.com'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


def normalized(text: str) -> str:
    return ' '.join(unicodedata.normalize('NFC', text).split())


class Node:
    def __init__(self, tag: str, attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children: list[Node | str] = []

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def text(self) -> str:
        return ''.join(child.text() if isinstance(child, Node) else child for child in self.children)

    def has(self, name: str) -> bool:
        return name in (self.attrs.get('class') or '').split()

    def select(self, tag=None, cls=None):
        return [node for node in self.walk() if (tag is None or node.tag == tag) and (cls is None or node.has(cls))]


class Document(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.root = Node('document')
        self.stack = [self.root]
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1], help='site root (default: parent of tools/)')
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    documents: dict[Path, Node] = {}
    sources: dict[Path, str] = {}
    styles: set[Path] = set()

    def check(condition, message):
        if not condition:
            errors.append(message)

    def document(path: Path):
        if path not in documents:
            sources[path] = path.read_text(encoding='utf-8')
            documents[path] = Document(sources[path]).root
        return documents[path]

    def local_reference(value: str, owner: Path, anchor=True):
        value = value.strip()
        if not value:
            return
        try:
            parts = urlsplit(value)
        except ValueError:
            errors.append(f'{owner.relative_to(root)}: malformed reference {value}')
            return
        if parts.scheme or parts.netloc:
            return
        name = unquote(parts.path)
        target = (root / name.lstrip('/') if name.startswith('/') else owner.parent / name).resolve() if name else owner
        if target.is_dir():
            target /= 'index.html'
        if not target.exists() and not target.suffix:
            target = target.with_suffix('.html')
        if not target.is_relative_to(root):
            errors.append(f'{owner.relative_to(root)}: reference escapes site root: {value}')
            return
        if not target.is_file():
            errors.append(f'{owner.relative_to(root)}: missing local reference {value}')
            return
        if target.suffix == '.css':
            styles.add(target)
        if anchor and parts.fragment and target.suffix in ('.html', '.htm'):
            ids = {node.attrs['id'] for node in document(target).walk() if node.attrs.get('id')}
            check(unquote(parts.fragment) in ids, f'{owner.relative_to(root)}: missing anchor {value}')

    canonical_urls = []
    for filename in PAGES:
        path = root / filename
        if not path.is_file():
            errors.append(f'Missing page: {filename}')
            continue
        doc = document(path)
        nodes = list(doc.walk())
        ids = Counter(node.attrs['id'] for node in nodes if node.attrs.get('id'))
        check(not [key for key, count in ids.items() if count > 1], f'{filename}: duplicate IDs: {[key for key, count in ids.items() if count > 1]}')
        check(len(doc.select('h1')) == 1, f'{filename}: expected exactly one h1')
        mains = doc.select('main')
        check(len(mains) == 1 and mains[0].attrs.get('id') and mains[0].attrs.get('tabindex') == '-1', f'{filename}: expected one focusable main landmark with an ID')
        active = [node for nav in doc.select('nav') for node in nav.select('a') if node.attrs.get('aria-current') == 'page']
        check(len(active) == (0 if filename == 'index.html' else 1), f'{filename}: incorrect active navigation count')
        if active:
            check(urlsplit(active[0].attrs.get('href', '')).path == filename, f'{filename}: active navigation targets another page')

        meta = {node.attrs.get('name') or node.attrs.get('property'): node.attrs.get('content', '') for node in doc.select('meta')}
        check(bool(meta.get('description', '').strip()), f'{filename}: missing description')
        canonicals = [node.attrs.get('href', '') for node in doc.select('link') if 'canonical' in (node.attrs.get('rel') or '').split()]
        expected = ORIGIN + ('/' if filename == 'index.html' else '/' + filename)
        check(canonicals == [expected], f'{filename}: expected canonical {expected}')
        canonical_urls.extend(canonicals)
        for key in ('og:title', 'og:description', 'og:image', 'og:type', 'og:url'):
            check(bool(meta.get(key, '').strip()), f'{filename}: missing {key}')
        check(meta.get('og:url') == expected, f'{filename}: og:url differs from canonical')
        check(len(doc.select('title')) == 1 and bool(doc.select('title')[0].text().strip()), f'{filename}: missing/duplicate title')
        check(not re.search(r'/original/|/workspace/|__RESOURCE_|(?:explore|review-iteration)-\d+\.html|cdn\.tailwindcss\.com', sources[path]), f'{filename}: leftover prototype path or Tailwind CDN')

        for node in nodes:
            for attr in ('href', 'src'):
                if node.attrs.get(attr):
                    local_reference(node.attrs[attr], path)
            if node.attrs.get('srcset') and not node.attrs['srcset'].startswith('data:'):
                for candidate in node.attrs['srcset'].split(','):
                    local_reference(candidate.strip().split()[0], path)
            if node.tag == 'img':
                check('alt' in node.attrs, f'{filename}: image lacks alt: {node.attrs.get("src")}')
                for dimension in ('width', 'height'):
                    check(str(node.attrs.get(dimension, '')).isdigit() and int(node.attrs[dimension]) > 0, f'{filename}: image lacks positive {dimension}: {node.attrs.get("src")}')
            for attr in ('aria-controls', 'aria-labelledby', 'aria-describedby'):
                for reference in (node.attrs.get(attr) or '').split():
                    check(reference in ids, f'{filename}: {attr} refers to missing #{reference}')

    checked_styles = set()
    while styles - checked_styles:
        path = next(iter(styles - checked_styles))
        checked_styles.add(path)
        css = path.read_text(encoding='utf-8')
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        for value in re.findall(r'url\(\s*([^)]*?)\s*\)', css):
            local_reference(value.strip('\'"'), path, anchor=False)
        for value in re.findall(r'@import\s+[\'"]([^\'"]+)[\'"]', css):
            local_reference(value, path, anchor=False)
    all_css = '\n'.join(path.read_text(encoding='utf-8') for path in checked_styles)
    fallback = r'html\s*:\s*not\(\s*\.js\s*\)[^{]*\bnav\s*\{[^}]*display\s*:\s*flex'
    check(bool(re.search(fallback, all_css, re.S)), 'CSS: missing readable mobile navigation fallback for html:not(.js)')
    check(len(canonical_urls) == len(set(canonical_urls)), 'Canonical URLs are not unique')
    check((root / '.nojekyll').is_file(), 'Missing .nojekyll for the static GitHub Pages site')

    counts = {'pages': len([root / name for name in PAGES if (root / name).is_file()]), 'stylesheets': len(checked_styles)}
    data_path = root / 'data/publications.json'
    if not data_path.is_file():
        errors.append('Missing data/publications.json')
    elif root / 'publications.html' in documents:
        try:
            papers = json.loads(data_path.read_text(encoding='utf-8'))
            check(isinstance(papers, list), 'Publication data must be an array')
            if isinstance(papers, list):
                articles = documents[root / 'publications.html'].select('article', 'paper')
                indexed = {node.attrs.get('data-index'): node for node in articles}
                check(len(articles) == len(papers) == len(indexed), 'Static publication article count does not match JSON records')
                for index, paper in enumerate(papers):
                    article = indexed.get(str(index))
                    if article is None:
                        errors.append(f'Publication {index}: missing static article')
                        continue
                    for key, tag, cls in [('title', 'h3', None), ('authors', None, 'authors-text'), ('venue', None, 'paper-venue')]:
                        matching = article.select(tag, cls)
                        check(bool(matching) and normalized(matching[0].text()) == normalized(paper[key]), f'Publication {index}: {key} differs from JSON')
                    if paper.get('abstract'):
                        panels = article.select(cls='abstract-panel')
                        paragraphs = panels[0].select('p') if panels else []
                        check(bool(paragraphs) and normalized(paragraphs[0].text()) == normalized(paper['abstract']), f'Publication {index}: abstract differs from JSON')
                    anchors = {node.attrs.get('href') for node in article.select('a')}
                    for link in paper['links']:
                        check(link['href'] in anchors, f'Publication {index}: missing resource {link["href"]}')
                counts.update(publications=len(papers), publication_links=sum(len(paper['links']) for paper in papers))
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'Invalid publication content/data: {exc}')

    talks = documents.get(root / 'talks.html')
    home = documents.get(root / 'index.html')
    patents = documents.get(root / 'patents.html')
    if talks:
        counts['talks'] = len(talks.select('article', 'talk-archive-entry'))
    if patents:
        counts['patents'] = len(patents.select('article', 'patent-entry'))
    if home and talks:
        for section in home.select(cls='upcoming-talks'):
            cards = section.select('a', 'upcoming-card')
            for card in cards:
                href = card.attrs.get('href')
                matching = [article for article in talks.select('article', 'talk-archive-entry') if href in {a.attrs.get('href') for a in article.select('a')}]
                check(len(matching) == 1, 'Homepage upcoming event must have one matching Talks archive entry')
                if matching:
                    ends = [node.attrs['data-upcoming-until'] for node in matching[0].walk() if node.attrs.get('data-upcoming-until')]
                    end = section.attrs.get('data-upcoming-until') or card.attrs.get('data-upcoming-until')
                    try:
                        check(bool(end) and any(datetime.fromisoformat(value.replace('Z', '+00:00')) == datetime.fromisoformat(end.replace('Z', '+00:00')) for value in ends), 'Homepage upcoming expiry differs from matching Talks entry')
                    except ValueError:
                        errors.append('Upcoming event has an invalid ISO expiry timestamp')

    if errors:
        print(f'Site check failed ({len(errors)} issues):', file=sys.stderr)
        for error in errors:
            print('  - ' + error, file=sys.stderr)
        return 1
    print('Site check passed: ' + ', '.join(f'{value} {key.replace("_", " ")}' for key, value in counts.items()) + '.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
