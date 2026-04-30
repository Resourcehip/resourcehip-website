---
title: Methodology
page_description: How the HIP Score is calculated — data sources, scoring dimensions, AI pipeline, and version history.
active_page: methodology
---

# Scoring Methodology

This page explains how every HIP Score is produced. Transparency about methodology is a core part of what makes a rating credible — and it is our strongest defence if a score is ever questioned.

**Current version: 1.3 · Effective April 2026**

---

## What the HIP Score measures

The HIP Score (Human Impact Profile Score) is a material resilience and sustainability rating, not a carbon footprint or general environmental endorsement. It assesses seven dimensions related to materials, supply chain, and end-of-life characteristics. See the [About page](/about) for a full summary.

---

## How the score is calculated

### Step 1 — Score each dimension independently

Each of the seven dimensions is assessed separately using a structured scoring rubric — a set of written criteria for each score band (0–2, 3–4, 5–6, 7–8, 9–10). The rubric for each dimension is defined in `methodology.yaml` (link below).

### Step 2 — Normalise the Regenerative Index

The RI uses a scale of −10 to +10. Before weighting, it is normalised to 0–10 using:

> **RI Normalised = (RI Raw + 10) ÷ 2**

This maps −10 → 0, 0 → 5, +10 → 10.

### Step 3 — Calculate the weighted HIP Score

> **HIP Score = (MSI × 0.20) + (SCR × 0.18) + (RC × 0.18) + (R × 0.13) + (SEI × 0.08) + (PL × 0.08) + (RI_norm × 0.15)**

The result is rounded to one decimal place.

---

## Dimension weights

| Code | Dimension | Weight | Scale |
|------|-----------|--------|-------|
| MSI | Material Scarcity Index | 20% | 0–10 |
| SCR | Supply Chain Risk | 18% | 0–10 |
| RC | Recyclability & Circularity | 18% | 0–10 |
| R | Repairability | 13% | 0–10 |
| SEI | Social & Environmental Impact | 8% | 0–10 |
| PL | Product Longevity | 8% | 0–10 |
| RI | Regenerative Index | 15% | −10 to +10 * |

*\* Normalised to 0–10 before weighting using the formula above.*

---

## HIP Mark tiers

The HIP Mark is awarded when the HIP Score meets a minimum threshold:

| Tier | Minimum HIP Score | RI Requirement |
|------|-------------------|----------------|
| HIP Mark Standard | 6.0 | None |
| HIP Mark Silver | 7.5 | None |
| HIP Mark Gold | 9.0 | RI raw ≥ +6.0 (Regenerative) |

Products scoring below 6.0 receive a HIP Score on the rating page but do not carry the HIP Mark.

Manufacturers holding a current verified rating and signed licence may display the HIP Mark. See the [Brand Guidelines](/methodology/hip-mark-brand-guidelines) for visual standards, permitted usage, and licensing requirements.

---

## Generic vs verified ratings

**Category (generic) ratings** are produced using publicly available data only. They rate a product category — not a specific named product — and apply conservative assumptions wherever data is missing. The result is an honest baseline for the category.

**Verified ratings** are produced using data submitted by the manufacturer through the Resourcehip submission form. Submitted data replaces the conservative category defaults. Scores above 5 on the Social & Environmental Impact dimension require third-party audit evidence — self-reported claims alone cannot exceed 5.

Where a verified rating uses a category default for a dimension (because no specific data was submitted for that dimension), this is clearly noted as an improvement opportunity on the rating page.

---

## The AI scoring pipeline

Ratings are produced using a local AI pipeline running on Resourcehip's own hardware using [Ollama](https://ollama.ai). **No product data is sent to external cloud AI services.**

| Component | Role |
|-----------|------|
| Model — qwen3.5:35b | Handles all scoring (all 7 dimensions) and all consumer prose generation |
| Temperature | 0.1 — produces consistent, reproducible outputs |
| Human review | Every rating reviewed and approved before publication |

No rating is ever published automatically without human sign-off.

---

## Data sources { #data-sources }

The following public data sources are used across ratings. Each rating page lists the specific sources used for that assessment.

| Source | Used for |
|--------|----------|
| [USGS Mineral Resources Program](https://www.usgs.gov/programs/mineral-resources-program) | Global reserve estimates and supply-risk designations |
| [EU Critical Raw Materials List (2023)](https://single-market-economy.ec.europa.eu/sectors/raw-materials/areas-specific-interest/critical-raw-materials_en) | EU high-importance, high-risk material designations |
| [World Bank Worldwide Governance Indicators](https://www.worldbank.org/en/publication/worldwide-governance-indicators) | Country political stability scores for supply chain risk |
| [iFixit Repairability Database](https://www.ifixit.com/repairability) | Standardised repairability scores for consumer products |
| [Ellen MacArthur Foundation](https://www.ellenmacarthurfoundation.org/) | Circular economy metrics and design-for-circularity benchmarks |
| [UK WRAP](https://www.wrap.ngo/) | UK material recycling rates and kerbside collection data |
| [Regenerative Organic Certified (ROC)](https://regenorganic.org/) | Verified regenerative agricultural certifications |

All data sources are public domain or published under open data licences. Attribution is shown on each rating page.

---

## Conservative by design

Where data is missing, the pipeline uses the most conservative reasonable assumption — not the most optimistic. This protects the integrity of the rating and creates a genuine incentive for manufacturers to submit better data. A verified rating with real data almost always scores higher than the category default.

---

## Methodology version history

| Version | Date | Key changes |
|---------|------|-------------|
| 1.3 | April 2026 | Clarified RI scoring criteria; updated Depleting vs Extractive band definitions and added worked examples to the scoring rubric. |
| 1.1 | March 2026 | Added Regenerative Index (RI) as seventh dimension. Adjusted weights: MSI 20%, SCR 18%, RC 18%, R 13%, SEI 8%, PL 8%, RI 15%. |
| 1.0 | February 2026 | Initial six-dimension methodology. |

---

## Licence and source

The HIP Score methodology is published under [Creative Commons CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — free to share and adapt for non-commercial purposes with attribution to Resourcehip.

The authoritative source file is `methodology.yaml`, maintained in the Resourcehip pipeline repository. <!-- Link to GitHub repository will be added when repository is made public. -->

The HIP Mark logo and Resourcehip brand are proprietary and may not be used without a licence.

---

## Dispute a rating

If you believe a rating contains an error, see the [Dispute a Rating](/dispute) page for the review process.

---

*Methodology v1.3 · Resourcehip Ltd · [Terms](/terms) · [Privacy](/privacy)*
