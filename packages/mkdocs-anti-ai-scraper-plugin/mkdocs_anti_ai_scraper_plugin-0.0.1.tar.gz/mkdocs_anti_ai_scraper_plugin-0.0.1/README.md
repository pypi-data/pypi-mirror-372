# MkDocs Anti AI Scraper Plugin

This plugin tries to prevent AI scrapers from easily ingesting your website's contents.
It is probably implemented pretty badly and by design it can be bypassed by anyone that invests a bit of time, but it is probably better than nothing.

## Installation



## Implemented Techniques

### robots.txt

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
Many bots may just ignore it ((Source)[https://www.tomshardware.com/tech-industry/artificial-intelligence/several-ai-companies-said-to-be-ignoring-robots-dot-txt-exclusion-scraping-content-without-permission-report]).

## Planned Techniques

- Encoding the page contents and decode with JS: Will prevent basic HTML parsers from getting the contents, but anything using a browser (selenium, pupeteer, etc) will still work.
- Encrypt page contents and adding client side "CAPTCHA" to generate the key: Should help against primitive browser based bots.
    It would probably make sense to just let the user solve the CAPTCHA once and cache the key as a cookie or in `localStorage`.
- Bot detection JS: Will be a cat and mouse game, but should help against badly written crawlers

Suggestions welcome: If you know bot detection mechanisms, that can be used with static websites, feel free to open an issue :D

## Problems and Considerations

- Similar to the encryption plugin, the encryption of the search index is hard.
    So best disable search to prevent anyone from accessing it.
- Obviously, to protect your contents from scraping, you should not have their source code hosted in public repos ;D
- By blocking bots, you also prevent search engines like Google from properly endexing your site.

## Development Commands

Clone repo:
```bash
git clone git@github.com:six-two/mkdocs-anti-ai-scraper-plugin.git
```

Install extension locally:
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



