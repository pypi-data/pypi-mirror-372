# MkDocs Anti AI Scraper Plugin

This plugin tries to prevent AI scrapers from easily ingesting your website's contents.
It is probably implemented pretty badly and by design it can be bypassed by anyone that invests a bit of time, but it is probably better than nothing.

## Installation

Install the plugin with `pip`:
```bash
pip install mkdocs-anti-ai-scraper-plugin
```

Then add the plugin to your `mkdocs.yml`:
```yaml
plugins:
- search
- anti_ai_scraper
```

Or with all config options:
```yaml
plugins:
- search
- anti_ai_scraper:
    robots_txt: True
    sitemap_xml: True
    encode_html: True
    debug: False
```

## Implemented Techniques

Technique | Scraper Protection | Impact on human visitors | Enabled by default
--- | --- | ---
Add robots.txt | weak | none | yes
Remove sitemap.xml | very weak | none | yes
Encode HTML | only against simple HTML parser based scrapers | slows down page loading, may break page events | true

### Add robots.txt

This technique is enabled by default, and can be disabled by setting the option `robots_txt: False` in `mkdocs.yml`.
If enabled, it adds a `robots.txt` with the following contents to the output directory:
```
User-agent: *
Disallow: /
```
This hints to crawlers that they should not crawl your site.

This technique does not hinder normal users from using the site at all.
However, the `robots.txt` is not enforcing anything.
It just tells well-behaved bots how you would like them to behave.
Many AI bots may just ignore it ([Source](https://www.tomshardware.com/tech-industry/artificial-intelligence/several-ai-companies-said-to-be-ignoring-robots-dot-txt-exclusion-scraping-content-without-permission-report)).

### Remove sitemap.xml

This technique is enabled by default, and can be disabled by setting the option `robots_txt: False` in `mkdocs.yml`.
If enabled, it removes the `sitemap.xml` and `sitemap.xml.gz` files.
This prevents leaking the paths to pages not referenced by your navigation.

### Encode HTML

This technique is enabled by default, and can be disabled by setting the option `robots_txt: False` in `mkdocs.yml`.
If enabled, it encodes (zip + ASCII85) each page's contents and will decode it in the user's browser with JavaScript.
This obscures the page contents to simple scrapers that just download and parse your HTML.
It will not work against any bots that use remote controlled browsers (using selenium or other tech).

The decoding takes some time and will result in browser events (like `onload`) being fired before the page is decoded.
This may break some functionality, that listens to these events and expects them to happen.

## Planned Techniques

- remove sitemap.xml(.gz): just obscures a bit, the nav will still point to most pages.
- Encoding the page contents and decode with JS: Will prevent basic HTML parsers from getting the contents, but anything using a browser (selenium, pupeteer, etc) will still work.
- Encrypt page contents and adding client side "CAPTCHA" to generate the key: Should help against primitive browser based bots.
    It would probably make sense to just let the user solve the CAPTCHA once and cache the key as a cookie or in `localStorage`.
- Bot detection JS: Will be a cat and mouse game, but should help against badly written crawlers

Suggestions welcome: If you know bot detection mechanisms, that can be used with static websites, feel free to open an issue :D

## Problems and Considerations

- Similar to the [encryption plugin](https://github.com/unverbuggt/mkdocs-encryptcontent-plugin), the encryption of the search index is hard.
    So best disable search to prevent anyone from accessing its index.
- Obviously, to protect your contents from scraping, you should not have their source code hosted in public repos ;D
- By blocking bots, you also prevent search engines like Google from properly endexing your site.

## Notable changes

### Version 0.1.0

- Added `encode_html` option
- Added `sitemap_xml` option

### Version 0.0.1

- Added `robots_txt` option

## Development Commands

This repo is managed using [poetry](https://github.com/python-poetry/poetry?tab=readme-ov-file).
You can install `poetry` with `pip install poetry` or `pipx install poetry`.

Clone repo:
```bash
git clone git@github.com:six-two/mkdocs-anti-ai-scraper-plugin.git
```

Install/update extension locally:
```bash
poetry install
```

Build test site:
```bash
poetry run mkdocs build
```

Serve test site:
```bash
poetry run mkdocs serve
```

### Release

Set PyPI API token (only needed once):
```bash
poetry config pypi-token.pypi YOUR_PYPI_TOKEN_HERE
```

Build extension:
```bash
poetry build
```

Upload extension:
```bash
poetry publish
```

