# Contributing to Resourcehip

Thank you for your interest in contributing to the Resourcehip website. This guide covers how to set up the project locally, make changes, and submit a pull request.

## Prerequisites

- Python 3.11 or later
- Git

## Getting started

```bash
git clone https://github.com/Resourcehip/resourcehip-website.git
cd resourcehip-website
pip install -r requirements.txt
```

## Building the site

```bash
# Build the static site
python build.py

# Generate sitemap and robots.txt
python sitemap.py

# Watch mode (rebuilds on file changes)
python build.py --watch
```

Output goes to `dist/`. Open `dist/index.html` in a browser to preview.

## Project structure

| Path | Description |
|------|-------------|
| `ratings/` | Product rating `.md` files (YAML frontmatter + prose) |
| `pages/` | Static content pages (about, methodology, privacy, etc.) |
| `blog/` | Blog posts in Markdown |
| `templates/` | Jinja2 HTML templates |
| `assets/` | Images and brand materials |
| `build.py` | Static site builder |
| `sitemap.py` | Sitemap and robots.txt generator |
| `dist/` | Build output served by Cloudflare Pages |

## Making changes

1. Create a feature branch from `main`:
   ```bash
   git checkout -b your-branch-name
   ```

2. Make your changes, then build locally to verify:
   ```bash
   python build.py && python sitemap.py
   ```

3. Spot-check in a browser — open the pages you changed under `dist/` and confirm they render correctly.

4. Commit with a clear message in imperative present tense:
   ```
   Add privacy policy update for cookie consent
   Fix rating card layout on mobile viewports
   ```

## Submitting a pull request

1. Push your branch:
   ```bash
   git push origin your-branch-name
   ```

2. Open a pull request against `main` on GitHub.

3. In the PR description, explain what you changed and why. Include a screenshot if the change is visual.

4. A maintainer will review your PR. Every merge to `main` triggers an automatic deploy to [resourcehip.com](https://resourcehip.com).

## Code style

- Templates follow WCAG 2.1 AA accessibility guidelines.
- Self-hosted fonts only (no third-party CDN requests).
- Keep commit subjects under 72 characters.

## Reporting issues

Open an issue on GitHub with a clear description of the problem or suggestion. Include screenshots or browser console output if relevant.

## Licence

By contributing, you agree that your contributions will be licensed under the same terms as this project.
