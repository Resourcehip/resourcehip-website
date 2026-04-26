#!/usr/bin/env python3
"""
download_fonts.py — Download self-hosted Montserrat woff2 files
================================================================
Run this script ONCE to download the Montserrat font files needed
to self-host the font (removing the Google Fonts CDN dependency).

Usage (from the Resourcehip folder):
    python resourcehip_website\fonts\download_fonts.py

After running, the fonts/ directory will contain the .woff2 files.
The base.html.j2 template already references these local files.
You do NOT need to re-run this script unless the font files are lost.

Why self-host?
--------------
The Google Fonts CDN sends visitor IP addresses to Google's servers
with each font request. Under UK GDPR this constitutes a data transfer
to a third-party processor. Self-hosting avoids this entirely.
"""

import re
import sys
import os
import urllib.request

FONT_DIR = os.path.dirname(os.path.abspath(__file__))

# Google Fonts CSS2 API — requests woff2 for the weights Resourcehip uses
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Montserrat:ital,wght@0,300;0,400;0,600;0,700;1,300"
    "&display=swap"
)

# Friendly names for the weight+style combinations we want
WEIGHT_NAMES = {
    ("300", "normal"):  "Light",
    ("300", "italic"):  "LightItalic",
    ("400", "normal"):  "Regular",
    ("600", "normal"):  "SemiBold",
    ("700", "normal"):  "Bold",
}

# Google's unicode-range values that distinguish latin vs latin-ext
# (latin-ext blocks start at U+0100)
LATIN_EXT_MARKER = "U+0100"


def fetch_css(url):
    """Fetch the Google Fonts CSS with a modern browser User-Agent so we get woff2 URLs."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")


def parse_font_faces(css):
    """
    Parse @font-face blocks from Google Fonts CSS.
    Returns list of dicts: {weight, style, subset, url}
    """
    # Split on @font-face boundaries
    blocks = re.split(r"@font-face\s*\{", css)
    fonts = []
    for block in blocks[1:]:  # skip text before first @font-face
        # Extract fields
        weight_m  = re.search(r"font-weight:\s*(\d+)", block)
        style_m   = re.search(r"font-style:\s*(\w+)", block)
        url_m     = re.search(r"url\(([^)]+\.woff2)\)", block)
        range_m   = re.search(r"unicode-range:\s*([^;}]+)", block)

        if not (weight_m and style_m and url_m):
            continue

        weight    = weight_m.group(1).strip()
        style     = style_m.group(1).strip()
        woff2_url = url_m.group(1).strip()
        urange    = range_m.group(1).strip() if range_m else ""

        subset = "latin-ext" if LATIN_EXT_MARKER in urange else "latin"

        fonts.append({
            "weight": weight,
            "style":  style,
            "subset": subset,
            "url":    woff2_url,
        })
    return fonts


def build_filename(weight, style, subset):
    """Build a friendly local filename, e.g. Montserrat-SemiBold-latin.woff2"""
    name = WEIGHT_NAMES.get((weight, style))
    if not name:
        name = f"w{weight}{'Italic' if style == 'italic' else ''}"
    return f"Montserrat-{name}-{subset}.woff2"


def download_file(url, dest, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)


def main():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    print("Fetching font list from Google Fonts...")
    try:
        css = fetch_css(GOOGLE_FONTS_URL)
    except Exception as e:
        print(f"  [error] Could not fetch Google Fonts CSS: {e}")
        print("  Check your internet connection and try again.")
        sys.exit(1)

    fonts = parse_font_faces(css)
    if not fonts:
        print("  [error] No @font-face blocks found in CSS response.")
        print("  The Google Fonts URL format may have changed.")
        sys.exit(1)

    print(f"  Found {len(fonts)} font variant(s) to download.\n")

    downloaded = 0
    skipped = 0
    failed = 0

    for f in fonts:
        filename = build_filename(f["weight"], f["style"], f["subset"])
        dest = os.path.join(FONT_DIR, filename)

        if os.path.exists(dest):
            print(f"  [skip]  {filename} (already exists)")
            skipped += 1
            continue

        try:
            size = download_file(f["url"], dest, headers)
            print(f"  [ok]    {filename} ({size // 1024}KB)")
            downloaded += 1
        except Exception as e:
            print(f"  [fail]  {filename}: {e}")
            failed += 1

    print(f"\nDone. {downloaded} downloaded, {skipped} skipped, {failed} failed.")

    if failed > 0:
        print("\nSome files failed. Check your internet connection and re-run.")
        print("Already-downloaded files will be skipped automatically.")
        sys.exit(1)
    elif downloaded > 0:
        print("\nNext step: rebuild the site.")
        print("  cd resourcehip_website")
        print("  python build.py")


if __name__ == "__main__":
    main()
