#!/usr/bin/env python3
"""
build.py — Resourcehip static site builder
==========================================
Reads .md rating files from ratings/ and .md page files from pages/,
renders them using Jinja2 templates, and outputs HTML to dist/.

Usage:
    python build.py [--watch]

Cloudflare Pages build command:
    pip install -r requirements.txt && python build.py

Output directory:  dist/
"""

import email.utils
import html as html_lib
import json
import re
import shutil
import sys
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import yaml
import markdown as md_lib
import jinja2
from markupsafe import Markup

from sitemap import html_files_to_urls, generate_sitemap, generate_robots

# ── Config ────────────────────────────────────────────────────────────────────

SITE_ROOT   = Path(__file__).parent

# Early adopter discount expiry. Pages with Jinja2 conditionals receive
# `today` and `discount_expires` so the build is date-aware. A scheduled
# rebuild on or after this date automatically removes the offer block.
DISCOUNT_EXPIRES = date(2026, 9, 30)
RATINGS_DIR = SITE_ROOT / "ratings"
PAGES_DIR   = SITE_ROOT / "pages"
BLOG_DIR    = SITE_ROOT / "blog"
TEMPLATES   = SITE_ROOT / "templates"
DIST        = SITE_ROOT / "dist"

# Static files to copy into dist/ root
STATIC_FILES = ["logo.png", "background.jpg", "index.html", "favicon.svg"]

# Static directories to copy wholesale into dist/
STATIC_DIRS = ["fonts", "assets"]

# Markdown extensions
MD_EXTENSIONS = ["tables", "fenced_code", "nl2br", "attr_list"]

# ── Jinja2 env ────────────────────────────────────────────────────────────────

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATES)),
    autoescape=jinja2.select_autoescape(["html"]),
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_md_file(filepath: Path) -> tuple[dict, str]:
    """Parse a Markdown file with YAML frontmatter.
    Returns (frontmatter_dict, html_body).
    """
    text = filepath.read_text(encoding="utf-8")

    # Split on --- delimiters
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1]) or {}
            body_md = parts[2].strip()
        else:
            frontmatter = {}
            body_md = text
    else:
        frontmatter = {}
        body_md = text

    # Strip Jinja2-style comments from body (<!-- ... -->) - keep HTML comments
    # Remove any leftover Jinja2 template tags (pipeline should have filled these)
    body_md = re.sub(r"\{%-?.*?-?%\}", "", body_md, flags=re.DOTALL)
    body_md = re.sub(r"\{\{.*?\}\}", "", body_md, flags=re.DOTALL)

    body_html = md_lib.markdown(body_md, extensions=MD_EXTENSIONS)
    return frontmatter, body_html


def _encode_email(addr: str) -> str:
    """Entity-encode every character of addr to deter address harvesting."""
    return ''.join(f'&#{ord(c)};' for c in addr)


def obfuscate_emails(html: str) -> str:
    """Replace all email addresses in rendered HTML with HTML entity encoding.

    Encodes mailto: href values first, then remaining plain-text addresses.
    Browsers decode entities transparently so links remain functional.
    """
    html = re.sub(
        r'(mailto:)([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
        lambda m: m.group(1) + _encode_email(m.group(2)),
        html,
    )
    html = re.sub(
        r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
        lambda m: _encode_email(m.group(1)),
        html,
    )
    return html


def slug_from_path(filepath: Path) -> str:
    """Generate a URL slug from a filename, e.g. hair_dryers.md → hair-dryers"""
    name = filepath.stem
    # Remove leading date prefix if present (e.g. 20240401_...)
    name = re.sub(r"^\d{8}_", "", name)
    return name.replace("_", "-").lower()


def hip_label(score: float) -> str:
    if score >= 9.0: return "Excellent"
    if score >= 7.0: return "Good"
    if score >= 5.0: return "Moderate"
    if score >= 3.0: return "Caution"
    return "Poor"


def rating_link(slug: str, label: str | None = None) -> "jinja2.Markup":
    """Return an HTML anchor to the category rating page. Safe for Jinja2 autoescaping."""
    display = label or (slug.replace("-", " ").title() + " HIP Rating")
    return Markup(
        f'<a href="/ratings/{slug}" class="rating-link">{display} →</a>'
    )


jinja_env.globals["rating_link"] = rating_link


# ── Build steps ───────────────────────────────────────────────────────────────

def build_ratings() -> list[dict]:
    """Build all rating pages. Returns list of rating metadata for the index."""
    template = jinja_env.get_template("rating.html.j2")
    out_dir = DIST / "ratings"
    out_dir.mkdir(parents=True, exist_ok=True)

    index_entries = []

    # Walk recursively so verified ratings under manufacturers/<brand>/ are found.
    # Mirror each markdown file's relative path into dist/ratings/ so the public
    # URL matches the source layout (decided 2026-04-18, Decisions/index in vault).
    for md_file in sorted(RATINGS_DIR.rglob("*.md")):
        data, body_html = parse_md_file(md_file)

        if not data:
            print(f"  [skip] {md_file.relative_to(RATINGS_DIR)} — no frontmatter")
            continue

        rel_path = md_file.relative_to(RATINGS_DIR)     # e.g. kettles.md OR manufacturers/tester/t-100.md
        slug = data.get("slug") or slug_from_path(md_file)
        data.setdefault("slug", slug)
        data.setdefault("methodology_version", "1.3")
        data.setdefault("hip_label", hip_label(data.get("hip_score", 0)))

        html = template.render(
            **data,
            body=body_html,
            page_title=data.get("title", "Rating"),
            page_description=data.get("consumer_summary", ""),
            active_page="ratings",
        )

        out_file = out_dir / rel_path.with_suffix(".html")
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(html, encoding="utf-8")
        print(f"  [rating] {out_file.relative_to(DIST)}")

        # Collect for index — include the extension-less URL path so the
        # catalogue can link to verified ratings at their manufacturer subpath.
        # (Cloudflare Pages rewrites /foo → /foo.html; we match that convention.)
        data["url_path"] = str(rel_path.with_suffix(""))
        index_entries.append(data)

    return index_entries


def build_ratings_index(entries: list[dict]) -> None:
    """Build /ratings/index.html — the catalogue page."""
    template = jinja_env.get_template("ratings_index.html.j2")
    # Sort by assessment date descending (newest first)
    entries_sorted = sorted(entries, key=lambda r: r.get("assessment_date", ""), reverse=True)
    html = template.render(
        ratings=entries_sorted,
        page_title="All Ratings",
        page_description="Human Impact Profiles for everyday product categories.",
        active_page="ratings",
    )
    out_file = DIST / "ratings" / "index.html"
    out_file.write_text(html, encoding="utf-8")
    print("  [index]  ratings/index.html")


def parse_page_file(filepath: Path, render_vars: dict | None = None) -> tuple[dict, str]:
    """Parse a page Markdown file with YAML frontmatter.
    Renders Jinja2 expressions in the body before converting to HTML so that
    pages can use conditionals like {% if today <= discount_expires %}.
    """
    text = filepath.read_text(encoding="utf-8")

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1]) or {}
            body_md = parts[2].strip()
        else:
            frontmatter = {}
            body_md = text
    else:
        frontmatter = {}
        body_md = text

    body_md = jinja2.Template(body_md).render(**(render_vars or {}))
    body_html = md_lib.markdown(body_md, extensions=MD_EXTENSIONS)
    return frontmatter, body_html


def build_pages() -> None:
    """Build static content pages from pages/**/*.md"""
    template = jinja_env.get_template("static_page.html.j2")

    if not PAGES_DIR.exists():
        print("  [info] No pages/ directory found — skipping static pages")
        return

    # Map top-level path component → active_page nav highlight
    active_map = {"about": "about", "methodology": "methodology"}

    page_render_vars = {
        "today": date.today(),
        "discount_expires": DISCOUNT_EXPIRES,
    }

    for md_file in sorted(PAGES_DIR.rglob("*.md")):
        data, body_html = parse_page_file(md_file, render_vars=page_render_vars)
        body_html = obfuscate_emails(body_html)
        rel_path = md_file.relative_to(PAGES_DIR)

        # Top-level component: filename stem for flat pages, dir name for nested
        top_part = rel_path.parts[0]
        top_slug = (top_part[:-3] if top_part.endswith(".md") else top_part).replace("_", "-").lower()

        # Remove active_page from data if present in frontmatter (avoid duplicate keyword arg)
        render_data = {k: v for k, v in data.items() if k != "active_page"}
        active_page_value = data.get("active_page") or active_map.get(top_slug, "")

        html = template.render(
            **render_data,
            body=body_html,
            page_title=data.get("title", md_file.stem.replace("-", " ").title()),
            active_page=active_page_value,
        )

        out_file = (DIST / rel_path).with_suffix(".html")
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(html, encoding="utf-8")
        print(f"  [page]   {out_file.relative_to(DIST)}")


def copy_static() -> None:
    """Copy static assets (logo, background, index.html, favicon) to dist/."""
    DIST.mkdir(parents=True, exist_ok=True)
    for name in STATIC_FILES:
        src = SITE_ROOT / name
        if src.exists():
            shutil.copy2(src, DIST / name)
            print(f"  [copy]   {name}")
        else:
            print(f"  [warn]   {name} not found — skipped")

    # Copy static directories (fonts/, etc.) wholesale
    for dirname in STATIC_DIRS:
        src_dir = SITE_ROOT / dirname
        dst_dir = DIST / dirname
        if src_dir.exists():
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            file_count = sum(1 for _ in dst_dir.iterdir())
            print(f"  [copy]   {dirname}/ ({file_count} files)")
        else:
            print(f"  [warn]   {dirname}/ not found — skipped")


class _LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.links.append(value)


def _link_resolves(href: str, dist_dir: Path) -> bool:
    path = href.split("?")[0].split("#")[0]
    if not path:
        return True
    clean = path.lstrip("/")
    if path.endswith("/"):
        return (dist_dir / clean / "index.html").exists()
    return (
        (dist_dir / (clean + ".html")).exists()
        or (dist_dir / clean / "index.html").exists()
        or (dist_dir / clean).exists()
    )


def validate_internal_links(dist_dir: Path) -> int:
    """Scan all built HTML files for broken internal hrefs. Returns count of unique broken links."""
    broken_seen: set[str] = set()
    broken_msgs: list[str] = []

    for html_file in sorted(dist_dir.rglob("*.html")):
        extractor = _LinkExtractor()
        try:
            extractor.feed(html_file.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue

        for href in extractor.links:
            if not href or not href.startswith("/"):
                continue
            if href.startswith(("http://", "https://", "//")):
                continue
            if href in broken_seen:
                continue
            if not _link_resolves(href, dist_dir):
                broken_seen.add(href)
                rel = html_file.relative_to(dist_dir)
                broken_msgs.append(f"  [broken-link] {href}  (first seen in {rel})")

    for msg in broken_msgs:
        print(msg, file=sys.stderr)
    return len(broken_seen)


def build_contact() -> None:
    """Build /contact.html from the dedicated contact form template."""
    template = jinja_env.get_template("contact.html.j2")
    html = template.render(
        page_title="Contact",
        page_description="Get in touch with Resourcehip about the HIP methodology, verified ratings, or the HIP Mark.",
        active_page="contact",
    )
    out_file = DIST / "contact.html"
    out_file.write_text(html, encoding="utf-8")
    print("  [page]   contact.html")


def copy_functions() -> None:
    """Copy Cloudflare Pages Functions to dist/ for deployment."""
    src = SITE_ROOT / "functions"
    dst = DIST / "functions"
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print("  [func]   functions/ copied")


def build_sitemap() -> None:
    """Generate sitemap.xml and robots.txt from freshly built dist/."""
    base_url = "https://resourcehip.com"
    urls = html_files_to_urls(DIST, base_url)
    (DIST / "sitemap.xml").write_text(generate_sitemap(urls), encoding="utf-8")
    print(f"  [sitemap] sitemap.xml ({len(urls)} URLs)")
    (DIST / "robots.txt").write_text(generate_robots(base_url), encoding="utf-8")
    print("  [sitemap] robots.txt")


def _parse_blog_post(filepath: Path) -> tuple[dict, str]:
    """Parse a blog Markdown file with YAML frontmatter.
    Processes Jinja2 calls in the body (e.g. {{ rating_link("kettles") }})
    before converting to HTML, so inline helpers work in post content.
    """
    raw = filepath.read_text(encoding="utf-8")

    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1]) or {}
            body_md = parts[2].strip()
        else:
            frontmatter = {}
            body_md = raw
    else:
        frontmatter = {}
        body_md = raw

    # Render Jinja2 expressions in body with autoescaping off (body is Markdown, not HTML).
    # rating_link() and any other helpers are injected as render vars.
    body_rendered = jinja2.Template(body_md).render(rating_link=rating_link)
    body_html = md_lib.markdown(body_rendered, extensions=MD_EXTENSIONS)
    return frontmatter, body_html


def build_blog(rating_slugs: set[str] | None = None) -> list[dict]:
    """Build blog post pages, index, category landing pages, and RSS feed."""
    if not BLOG_DIR.exists():
        print("  [info] No blog/ directory found — skipping blog build")
        return []

    blog_out = DIST / "blog"
    blog_out.mkdir(parents=True, exist_ok=True)

    posts_meta: list[tuple[dict, str]] = []

    for md_file in sorted(BLOG_DIR.glob("*.md")):
        data, body_html = _parse_blog_post(md_file)
        body_html = obfuscate_emails(body_html)

        if not data:
            print(f"  [skip] blog/{md_file.name} — no frontmatter")
            continue

        slug = data.get("slug") or slug_from_path(md_file)
        data.setdefault("slug", slug)
        data.setdefault("canonical_url", f"https://resourcehip.com/blog/{slug}")
        posts_meta.append((data, body_html))

    # Newest-first by last_updated
    posts_meta.sort(key=lambda x: str(x[0].get("last_updated", "")), reverse=True)

    # Individual post pages at /blog/<slug>/index.html (clean URLs)
    post_tmpl = jinja_env.get_template("blog_post.html.j2")
    for data, body_html in posts_meta:
        slug = data["slug"]
        html = post_tmpl.render(
            **data,
            body=body_html,
            page_title=data.get("title", slug),
            page_description=data.get("description", ""),
            active_page="blog",
        )
        post_dir = blog_out / slug
        post_dir.mkdir(parents=True, exist_ok=True)
        (post_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"  [blog]   blog/{slug}/index.html")

    # Blog index at /blog/index.html
    index_tmpl = jinja_env.get_template("blog_index.html.j2")
    index_html = index_tmpl.render(
        posts=[d for d, _ in posts_meta],
        page_title="Blog",
        page_description="Insights and buying guides from the Resourcehip team.",
        active_page="blog",
    )
    (blog_out / "index.html").write_text(index_html, encoding="utf-8")
    print("  [blog]   blog/index.html")

    # Category landing pages at /blog/category/<slug>/index.html
    categories: dict[str, list[dict]] = {}
    for data, _ in posts_meta:
        cat = data.get("category")
        if cat:
            categories.setdefault(cat, []).append(data)

    cat_tmpl = jinja_env.get_template("blog_category.html.j2")
    for cat_slug, cat_posts in sorted(categories.items()):
        cat_dir = blog_out / "category" / cat_slug
        cat_dir.mkdir(parents=True, exist_ok=True)
        html = cat_tmpl.render(
            category_slug=cat_slug,
            posts=cat_posts,
            rating_slugs=rating_slugs or set(),
            page_title=f"{cat_slug.replace('-', ' ').title()} — Blog",
            page_description=f"Articles and buying guides about {cat_slug.replace('-', ' ')} from Resourcehip.",
            active_page="blog",
        )
        (cat_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"  [blog]   blog/category/{cat_slug}/index.html")

    # RSS 2.0 feed at /blog/feed.xml
    _build_blog_rss(blog_out, posts_meta)

    return [d for d, _ in posts_meta]


def build_search_index(entries: list[dict] | None = None) -> None:
    """Generate /dist/search-index.json from rating metadata.

    Can be called standalone (parses .md files itself) or with pre-parsed
    entries from a full build.  Output is a compact JSON array consumed by
    the client-side search widget.
    """
    if entries is None:
        entries = []
        for md_file in sorted(RATINGS_DIR.rglob("*.md")):
            data, _ = parse_md_file(md_file)
            if not data:
                continue
            rel_path = md_file.relative_to(RATINGS_DIR)
            data["url_path"] = str(rel_path.with_suffix(""))
            entries.append(data)

    index = []
    for e in entries:
        rating_type = e.get("rating_type", "generic")
        brand = e.get("brand") or ""

        if rating_type == "verified" and brand == "Category Ceiling":
            search_type = "ceiling"
        elif rating_type == "verified":
            search_type = "manufacturer"
        else:
            search_type = "generic"

        summary = e.get("consumer_summary") or ""
        if len(summary) > 150:
            summary = summary[:147] + "..."

        item: dict = {
            "name": e.get("title", ""),
            "url": f"/ratings/{e.get('url_path', e.get('slug', ''))}",
            "hipScore": e.get("hip_score", 0),
            "hipLabel": e.get("hip_label", ""),
            "riScore": e.get("ri_score", 0),
            "riDescriptor": e.get("ri_descriptor", ""),
            "type": search_type,
            "category": e.get("category", ""),
        }
        if brand and search_type == "manufacturer":
            item["brand"] = brand
        if summary:
            item["summary"] = summary

        index.append(item)

    DIST.mkdir(parents=True, exist_ok=True)
    out_file = DIST / "search-index.json"
    out_file.write_text(
        json.dumps(index, indent=None, separators=(",", ":")),
        encoding="utf-8",
    )
    size_kb = out_file.stat().st_size / 1024
    print(f"  [search] search-index.json ({len(index)} entries, {size_kb:.1f} KB)")


def _build_blog_rss(blog_out: Path, posts_meta: list[tuple[dict, str]]) -> None:
    """Write /blog/feed.xml as RSS 2.0."""
    site_url = "https://resourcehip.com"
    items_xml = []

    for data, _ in posts_meta[:20]:
        slug = data["slug"]
        title = html_lib.escape(data.get("title", slug))
        link = f"{site_url}/blog/{slug}"
        description = html_lib.escape(data.get("description", ""))
        pub_raw = data.get("last_updated", "")
        try:
            dt = datetime.strptime(str(pub_raw), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            dt = datetime.now(timezone.utc)
        pub_date = email.utils.format_datetime(dt)
        items_xml.append(
            f"    <item>\n"
            f"      <title>{title}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <guid isPermaLink=\"true\">{link}</guid>\n"
            f"      <description>{description}</description>\n"
            f"      <pubDate>{pub_date}</pubDate>\n"
            f"    </item>"
        )

    build_date = email.utils.format_datetime(datetime.now(timezone.utc))
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        "    <title>Resourcehip Blog</title>\n"
        f"    <link>{site_url}/blog/</link>\n"
        "    <description>Insights, buying guides, and sustainability analysis from Resourcehip.</description>\n"
        "    <language>en-gb</language>\n"
        f"    <lastBuildDate>{build_date}</lastBuildDate>\n"
        f'    <atom:link href="{site_url}/blog/feed.xml" rel="self" type="application/rss+xml"/>\n'
        + "\n".join(items_xml)
        + "\n  </channel>\n</rss>"
    )
    (blog_out / "feed.xml").write_text(feed, encoding="utf-8")
    print("  [blog]   blog/feed.xml")


# ── Entry point ───────────────────────────────────────────────────────────────

def build():
    print("Building Resourcehip static site...\n")
    print("→ Copying static assets")
    copy_static()
    print("→ Building rating pages")
    index_entries = build_ratings()
    build_ratings_index(index_entries)
    rating_slugs = {e["slug"] for e in index_entries}
    print("→ Building static pages")
    build_pages()
    build_contact()
    print("→ Copying Cloudflare Pages Functions")
    copy_functions()
    print("→ Building blog")
    blog_posts = build_blog(rating_slugs=rating_slugs)
    print("→ Generating sitemap")
    build_sitemap()
    print("→ Validating internal links")
    broken = validate_internal_links(DIST)
    print(f"\nDone. Output in {DIST}/")
    print(f"  {len(index_entries)} rating(s) built")
    print(f"  {len(blog_posts)} blog post(s) built")
    if broken:
        print(f"  {broken} broken internal link(s) — see warnings above", file=sys.stderr)


if __name__ == "__main__":
    if "--search-index" in sys.argv:
        print("Generating search index...\n")
        build_search_index()
        print("\nDone.")
        sys.exit(0)

    if "--watch" in sys.argv:
        # Simple watch mode using polling (no watchdog dependency)
        import time
        print("Watch mode — rebuilding on file changes. Ctrl+C to stop.\n")
        last_mtimes: dict[str, float] = {}

        def get_mtimes():
            mtimes = {}
            for p in list(RATINGS_DIR.glob("*.md")) + list(TEMPLATES.glob("*.j2")):
                mtimes[str(p)] = p.stat().st_mtime
            if PAGES_DIR.exists():
                for p in PAGES_DIR.glob("*.md"):
                    mtimes[str(p)] = p.stat().st_mtime
            return mtimes

        while True:
            current = get_mtimes()
            if current != last_mtimes:
                build()
                last_mtimes = current
            time.sleep(2)
    else:
        build()
