# Nicola Piovesan — personal website

Static HTML, CSS and JavaScript, published through GitHub Pages at
<https://www.nicolapiovesan.com/>. No framework, package installation or build is
required to serve the site. `.nojekyll` keeps the files independent of the legacy
Jekyll theme setting.

## Local preview

From this directory:

```sh
python3 -m http.server 8000
```

Open `http://localhost:8000`. On Windows, `py -m http.server 8000` also works.

## Files

- `index.html`, `biography.html`, `publications.html`, `talks.html`, `patents.html`:
  the five public pages, including their readable content.
- `css/site.css`: shared typography, background, navigation and footer.
- `css/home.css`, `css/archive.css`, `css/biography.css`: page layouts.
- `js/`: progressive filters, shared navigation, contact reveal and event expiry.
- `data/publications.json`: the source of truth for publication records.
- `images/`: original photographs, the approved transparent portrait
  (`nicola-piovesan.png`) and the previous portrait mask. The homepage crops the
  new portrait in CSS, preserving its full source image.

The homepage applies the approved softer portrait tones through the
`portrait-tones` SVG filter in `index.html`, referenced by `css/home.css`.
The PNG and its transparency remain unchanged.

The publication archive is present in the HTML before JavaScript runs. JavaScript
adds search, filters, sorting and compact author lists. Abstracts use native
disclosures, so they remain accessible without JavaScript.

## Updating publications

Edit `data/publications.json`, retaining the fields used by existing records, then:

```sh
python3 tools/render_publications.py
python3 tools/render_publications.py --check
python3 tools/check_site.py
```

Commit both the JSON and regenerated `publications.html`. No server-side data
fetch or deployment-time generator is needed.

## Updating an upcoming talk

Edit the compact `.upcoming-talks` section in `index.html` and its matching archive
entry in `talks.html`. Update the year counts when adding an archive entry. Set
`data-upcoming-until` to the event's end timestamp with an explicit UTC offset on
both the homepage section and archive badge. After that instant, the homepage
announcement is hidden and the archive entry remains, labelled “Talk”. The check
also runs when returning to an open tab.

The current event uses `2026-11-18T15:00:00+02:00`, matching the confirmed
14:00–15:00 CEST (UTC+2) announcement.

## Contact and analytics

The homepage email is composed only after “Contact me” is activated. The encoded
address is in its `data-address` attribute; this limits basic address scraping,
not automated browsers that activate the control.

Existing Google Analytics and Clicky integrations are retained in
`js/analytics.js`. The `data-google-analytics` body attribute preserves the
original Google Analytics page scope; Clicky remains enabled on all five pages.

The original public image URLs, custom domain configuration and `notebooks/`
content remain available.
