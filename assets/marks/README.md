# HIP Mark — Badge File Pack

Files in this directory are the master mark assets for Resourcehip's three award tiers and five RI tier chips.
Generated from `pipeline/tools/generate_marks.py` (spec: [RES-84] brand guidelines, style guide §6).

## Tier badge files

| File | Purpose |
|------|---------|
| `hip-mark-standard.svg` | Standard tier badge (example score 7.0, #3a9e62) |
| `hip-mark-silver.svg` | Silver tier badge (example score 8.0, #7a9ab8) |
| `hip-mark-gold.svg` | Gold tier badge (example score 9.5, #c8920a) |
| `hip-mark-template.svg` | Blank/template — for pre-licence sample files |
| `hip-mark-{tier}-1024.png` | PNG, transparent background, 1024 px wide |
| `hip-mark-{tier}-512.png` | PNG, transparent background, 512 px wide |
| `hip-mark-{tier}-128.png` | PNG, transparent background, 128 px wide |
| `hip-mark-{tier}-64.png` | PNG, transparent background, 64 px wide |
| `hip-mark-{tier}-24.png` | PNG, transparent background, 24 px wide (favicon scale) |
| `hip-mark-{tier}.pdf` | PDF vector, 60 mm × 70.8 mm, for print artwork |

## RI tier chip files

| File | Purpose |
|------|---------|
| `ri-chip-depleting.svg` | RI tier 1/5 — Depleting (#c04040) |
| `ri-chip-extractive.svg` | RI tier 2/5 — Extractive (#c8920a) |
| `ri-chip-renewable.svg` | RI tier 3/5 — Renewable (#4FA9A5) |
| `ri-chip-restorative.svg` | RI tier 4/5 — Restorative (#7ab85a) |
| `ri-chip-regenerative.svg` | RI tier 5/5 — Regenerative (#3a9e62) |
| `ri-chip-{tier}-200.png` | PNG, 200 px wide |
| `ri-chip-{tier}-64.png` | PNG, 64 px wide |

## Geometry (per spec)

- Circular donut, **22 % stroke width**
- Arc fills clockwise from 12 o'clock, proportional to score
- Score field: one decimal place, centred
- Wordmark: **HIP** beneath score
- Authority line: `resourcehip.com` below the ring
- Font: Montserrat (Google Fonts); Ubuntu Sans fallback for offline rendering

## Tier colours

| Tier | Hex | Threshold |
|------|-----|-----------|
| Standard | `#3a9e62` | HIP ≥ 6.0 |
| Silver | `#7a9ab8` | HIP ≥ 7.5 |
| Gold | `#c8920a` | HIP ≥ 9.0 AND RI ≥ +6 |

## Per-licensee pack

When issuing a mark to a licensee, generate a new SVG/PNG/PDF with their exact score baked in:

```bash
python3 pipeline/tools/generate_marks.py   # regenerates masters
```

Edit `TIERS` dict in the script to set a product-specific score, or extend the script with
a `--score` / `--tier` CLI argument for one-off issuance.

## Minimum sizes (brand guidelines)

- Print / packaging: **12 mm** diameter
- Digital: **64 px** diameter

## Regenerating

```bash
# From the Resourcehip project root:
python3 pipeline/tools/generate_marks.py
```

Requires: `pycairo` (system package). Ubuntu Sans must be installed for offline PNG/PDF rendering.
For brand-exact Montserrat rendering in PNG/PDF: install the font via `sudo apt install fonts-montserrat`
and re-run.
