#!/usr/bin/env python3
"""Regenerate the readable publication archive from data/publications.json.

Run from any directory: python3 tools/render_publications.py
Use --check to verify that the checked-in HTML is up to date without writing it.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path
import re

ARROW = '<svg aria-hidden="true" class="external-icon" viewBox="0 0 16 16"><path d="M4 12 12 4M4 4h8v8" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>'
CHEVRON = '<svg aria-hidden="true" viewBox="0 0 10 10"><path d="m2 3.5 3 3 3-3" stroke="currentColor" fill="none" stroke-width="1.2"/></svg>'


def text(value: object) -> str:
    return escape(str(value), quote=True)


def authors_html(authors: str) -> str:
    return re.sub(r'Nicola Piovesan|N\. Piovesan', lambda m: '<strong>' + m[0] + '</strong>', text(authors))


def paper_html(paper: dict, index: int) -> str:
    title = text(paper['title'])
    badges = []
    type_class = re.sub(r'\s+', '-', paper['type'].lower())
    for badge in paper['badges']:
        if 'Award' in badge:
            badges.append('<span class="award-badge"><span aria-hidden="true">✧ </span>' + text(badge) + '</span>')
        else:
            badges.append('<span class="type-badge ' + text(type_class) + '">' + text(badge) + '</span>')
    first = paper['links'][0] if paper['links'] else None
    heading = ('<a class="paper-title-link" href="' + text(first['href']) + '" target="_blank" rel="noopener noreferrer">' + title + '</a>') if first else title
    links = ''.join('<a href="' + text(link['href']) + '" target="_blank" rel="noopener noreferrer" aria-label="' + text(link['label'] + ': ' + paper['title']) + '">' + text(link['label']) + ' ' + ARROW + '</a>' for link in paper['links'])
    abstract = ''
    abstract_button = ''
    if paper['abstract']:
        abstract_button = ('<button class="abstract-toggle abstract-button" type="button" aria-expanded="false" aria-controls="abstract-' + str(index) + '" aria-label="' + text('Abstract: ' + paper['title']) + '" hidden>Abstract ' + CHEVRON + '</button>')
        abstract = ('\n<details class="abstract-disclosure" id="abstract-' + str(index) + '"><summary class="abstract-summary" aria-label="' + text('Abstract: ' + paper['title']) + '">Abstract ' + CHEVRON + '</summary>'
                    '<div class="abstract-panel"><h4>Abstract</h4><p>' + text(paper['abstract']) + '</p></div></details>')
    return ('<article class="paper" data-type="' + text(paper['type']) + '" data-index="' + str(index) + '">\n'
            '<div class="paper-top"><h3>' + heading + '</h3><div class="paper-badges">' + ''.join(badges) + '</div></div>\n'
            '<p class="paper-venue">' + text(paper['venue']) + '</p>\n'
            '<div class="paper-bottom"><div class="paper-authors"><span class="authors-text" id="authors-' + str(index) + '">' + authors_html(paper['authors']) + '</span>'
            '<button class="authors-toggle" type="button" aria-expanded="false" aria-controls="authors-' + str(index) + '" aria-label="' + text('Show all authors: ' + paper['title']) + '" hidden>All authors</button></div>'
            '<div class="paper-actions">' + abstract_button + links + '</div></div>' + abstract + '\n</article>')


def archive_html(papers: list[dict]) -> str:
    years = sorted({str(paper['year']) for paper in papers}, key=int, reverse=True)
    result = []
    for year in years:
        items = [(index, paper) for index, paper in enumerate(papers) if str(paper['year']) == year]
        result.append('<section class="year-group" data-year="' + text(year) + '" aria-labelledby="heading-' + text(year) + '"><div class="group-heading"><h2 id="heading-' + text(year) + '">' + text(year) + '</h2><span class="group-count">' + str(len(items)) + '</span></div><div class="paper-list">\n' + '\n'.join(paper_html(paper, index) for index, paper in items) + '\n</div></section>')
    return '\n'.join(result)


def year_nav_html(papers: list[dict]) -> str:
    counts = Counter(str(paper['year']) for paper in papers)
    return ('<button class="year-button selected" type="button" data-year="all" aria-pressed="true">All years <span>' + str(len(papers)) + '</span></button>\n'
            + '\n'.join('<button class="year-button" type="button" data-year="' + text(year) + '" aria-pressed="false">' + text(year) + '<span>' + str(counts[year]) + '</span></button>' for year in sorted(counts, key=int, reverse=True)))


def year_options_html(papers: list[dict]) -> str:
    return '<option value="all">All years</option>\n' + '\n'.join('<option value="' + text(year) + '">' + text(year) + '</option>' for year in sorted({str(paper['year']) for paper in papers}, key=int, reverse=True))


def year_links_html(papers: list[dict]) -> str:
    counts = Counter(str(paper['year']) for paper in papers)
    return ('<a class="year-button" href="#results">All years <span>' + str(len(papers)) + '</span></a>\n'
            + '\n'.join('<a class="year-button" href="#heading-' + text(year) + '">' + text(year) + '<span>' + str(counts[year]) + '</span></a>' for year in sorted(counts, key=int, reverse=True)))


def replace_block(document: str, name: str, content: str) -> str:
    start = '<!-- ' + name + ':START -->'
    end = '<!-- ' + name + ':END -->'
    if document.count(start) != 1 or document.count(end) != 1:
        raise ValueError('Expected one pair of ' + name + ' markers in publications.html')
    return re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda _: start + '\n' + content + '\n' + end, document, count=1, flags=re.S)


def render(document: str, papers: list[dict]) -> str:
    document = replace_block(document, 'PUBLICATIONS', archive_html(papers))
    document = replace_block(document, 'YEAR_NAV', year_nav_html(papers))
    document = replace_block(document, 'YEAR_OPTIONS', year_options_html(papers))
    document = replace_block(document, 'YEAR_LINKS', year_links_html(papers))
    document = re.sub(r'(<span\b[^>]*\bdata-publication-total(?:="[^"]*")?[^>]*>).*?(</span>)', lambda m: m[1] + str(len(papers)) + m[2], document, flags=re.S)
    document = re.sub(r'(<p\b[^>]*\bid="result-count"[^>]*>).*?(</p>)', lambda m: m[1] + str(len(papers)) + (' publication' if len(papers) == 1 else ' publications') + m[2], document, count=1, flags=re.S)
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='check generated HTML without changing files')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1], help=argparse.SUPPRESS)
    args = parser.parse_args()
    data_path = args.root / 'data' / 'publications.json'
    path = args.root / 'publications.html'
    papers = json.loads(data_path.read_text())
    if not isinstance(papers, list):
        raise ValueError('publications.json must contain an array')
    document = path.read_text()
    generated = render(document, papers)
    if args.check:
        if generated != document:
            print('Publications HTML is out of date. Run python3 tools/render_publications.py.')
            return 1
        print('Publications HTML is up to date (' + str(len(papers)) + ' records).')
        return 0
    path.write_text(generated)
    print('Rendered ' + str(len(papers)) + ' publications into ' + str(path))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
