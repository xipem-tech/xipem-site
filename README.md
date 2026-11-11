# xipem.com

Static site for Xipem Digital Ltda: app policies, support pages and `app-ads.txt`. No marketing pages.

- `src/`: page sources (Markdown), `style.css`, `app-ads.txt`, `robots.txt`.
- `src/pages.txt`: pages built from Markdown that lives elsewhere (e.g. the Monlings privacy policy in `../monlings/docs/privacy-policy.md`, the source of truth).
- `python3 build.py` writes `docs/`; commit and push it. GitHub Pages serves `main` / `docs` at https://xipem.com (DNS at Hostinger points to GitHub Pages). The build reads the private Monlings repo, so it runs locally, not in CI.

Layout: `/games/<app>/privacy/`, `/games/<app>/support/` (`/apps/<app>/...` for non-game apps). One `app-ads.txt` at the root lists the AdMob publisher for every app.
