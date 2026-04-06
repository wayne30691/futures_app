Static deploy: upload the entire site/ folder.

This bundle contains:
- index.html
- data/market_1m.json
- manifest.json

Raw CSV files are NOT published.

Netlify Drop: https://app.netlify.com/drop
Cloudflare Pages: upload site/ contents so index.html stays at the root.
GitHub Pages: publish site/ contents from gh-pages or /docs.

Regenerate after updating raw/: python scripts/publish_raw_web.py
