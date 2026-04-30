---
title: "What is the HIP Score? A Plain-English Explainer"
slug: what-is-the-hip-score
category: methodology
description: "The HIP Score is a 0–10 rating of how a product is built, sourced, and recovered — not how it performs in use. Here is what each of the seven dimensions measures, and why the score moves where it does."
keywords: [HIP score, sustainability score, product rating methodology, Resourcehip, material resilience]
last_updated: 2026-04-28
canonical_url: https://resourcehip.com/blog/what-is-the-hip-score
author: Resourcehip Editorial
---

## What the HIP Score Is — And What It Is Not

The HIP Score is a single number from 0 to 10 that summarises how a product performs across seven dimensions of long-term material resilience. It is the headline figure on every Resourcehip rating page.

The HIP Score is not:

- a carbon-footprint estimate
- a measure of in-use energy efficiency
- a generalised "is this good for the environment" verdict
- a comparison between brands or models within a category

What it is:

- a measure of how the product is **built** (materials, repairability)
- a measure of how it is **sourced** (supply-chain risk and audit verification)
- a measure of how it is **recovered** at end of life (recyclability, take-back, regenerative inputs)
- a fixed, reproducible rubric — the same product, scored twice, gets the same score

The reference page at [`/methodology`](/methodology) is the authoritative document. This article is the plain-English version.

## The Seven Dimensions

Each dimension is scored independently from 0 to 10 against a published rubric. Six are weighted positive; one (the Regenerative Index) is normalised. The weights are not arbitrary — they reflect where the long-tail environmental cost of a consumer product actually sits.

### Material Scarcity Index (MSI) — weight 20%

How dependent is the product on materials that are scarce, geopolitically concentrated, or on the EU Critical Raw Materials list? A device built from recycled stainless steel and abundant minerals scores high. A device built around lithium, cobalt, neodymium, and rare earths from single-country supply scores low.

This is the biggest single weight in the score. The reason: scarcity decisions made at design time are essentially permanent. You can change recycling rates over time; you cannot un-bond a glued lithium battery into the housing.

### Supply Chain Risk (SCR) — weight 18%

Where do the materials come from, who audits the suppliers, and is the supply diversified? Cobalt from the DRC with no due-diligence framework scores low. Diversified sourcing across audited suppliers in the EU, Australia, and Japan scores high. Verified third-party audits (RBA, OECD due-diligence) move this dimension significantly.

### Recyclability and Circularity (RC) — weight 18%

What proportion of the product, by weight, can practically enter recycling streams at end of life? Glued, sealed, mixed-material devices score low. Screw-fastened, single-material, take-back-supported devices score high. **Theoretical** recyclability does not count — there has to be a real recovery path.

### Repairability (R) — weight 13%

Can a non-specialist repair the device with reasonable cost and effort? iFixit scores, screw-fastened construction, public service manuals, and a stocked spare-parts programme all push this dimension up. Glue, tamper-evident seals, and missing spare parts push it down.

### Social and Environmental Impact (SEI) — weight 8%

Are the manufacturing facilities audited for labour and environmental practice? RBA audits, ISO 14001 certifications, modern-slavery statements, and ILO compliance all contribute. Manufacturing in a higher-risk jurisdiction is not, by itself, a penalty — the absence of audit evidence is. Scores above 5 on this dimension require third-party audit evidence; self-reported claims cannot exceed 5.

### Product Longevity (PL) — weight 8%

How long is the product designed to last? Warranty length, IP rating, modular design, and stated software-support windows (where applicable) all feed in. A 2-year warranty + 4-year design life is a baseline score; a 5-year warranty + 12-year design life moves the dimension into the upper bands.

### Regenerative Index (RI) — weight 15%, scale −10 to +10

This is the only dimension where negative scores are valid. The RI measures whether a product *depletes* the systems it draws from (negative), neither depletes nor restores (around zero), or actively *restores* them (positive). The five canonical tiers are:

- **Depleting (−10 to −5)** — virgin extraction, no recycled content, no take-back, no regenerative inputs.
- **Extractive (−5 to −1)** — partial recycled content, possible take-back, but still net-extractive.
- **Renewable (0 to +3)** — substantial recycled content with verified take-back; closing the loop.
- **Restorative (+3 to +6)** — closed-loop material recovery + regenerative agricultural or biological inputs.
- **Regenerative (+6 to +10)** — third-party-certified ecosystem restoration evidence.

The RI is normalised to 0–10 before weighting, so a Depleting score of −7 contributes 1.5 to the weighted total; a Restorative score of +4 contributes 7.0. We have a [dedicated explainer](/blog/what-is-the-regenerative-index) on the RI specifically.

## How the Final Score is Calculated

The HIP Score is the weighted sum:

> **HIP Score = (MSI × 0.20) + (SCR × 0.18) + (RC × 0.18) + (R × 0.13) + (SEI × 0.08) + (PL × 0.08) + (RI_normalised × 0.15)**

Rounded to one decimal place. That is it. There is no judge's bonus, no editorial adjustment, no rounding-up to keep the manufacturer happy. The same input numbers always produce the same output.

## What Different Scores Mean

A HIP Score sits inside a category and should be read against the category baseline:

- **Below 3.0** — a typical mass-market product in a structurally compromised category. Most consumer-electronics categories have generic baselines in this range.
- **3.0 to 6.0** — material resilience is partial; some dimensions strong, others poor. No HIP Mark.
- **6.0 to 7.5** — earns the **Standard** HIP Mark. The product is materially honest, designed for repair, and has a credible end-of-life path.
- **7.5 to 9.0** — earns the **Silver** HIP Mark. Substantial recycled content, audited sourcing, and a long product life.
- **9.0 and above, with RI ≥ +6** — earns the **Gold** HIP Mark. Closed-loop material recovery and certified regenerative inputs.

The Gold threshold deliberately requires both a high HIP Score *and* a Regenerative Index in the Regenerative band. A product can be a Silver-grade engineering achievement without being regenerative; Gold is reserved for the combination.

## Generic vs Verified Ratings

Every product rating is one of two types:

- **Generic ratings** are produced from public data only and apply conservative assumptions wherever data is missing. They rate a product *category*, not a specific named product. Generic ratings sit at the category baseline.
- **Verified ratings** use evidence submitted by the manufacturer through the [submission form](/submit). Submitted data replaces conservative defaults. Verified ratings can climb up to the category ceiling.

The gap between baseline and ceiling is the **headroom** in a category — the space within which a manufacturer with credible evidence can demonstrate that they outperform the assumed-mass-market default. We have a [dedicated explainer](/blog/generic-vs-verified-ratings) on why this gap exists and what it represents.

## Why the HIP Score Is Built This Way

A sustainability rating that is easy to game is worse than no rating at all. Three design decisions specifically protect against gaming:

- **Conservative defaults.** Missing data lowers the score, never raises it. There is no incentive to be vague.
- **Audit-evidence floors.** SEI scores above 5 require third-party audit evidence. A manufacturer cannot self-report into the upper band.
- **Methodology transparency.** The full rubric is published. Anyone can see exactly which inputs would move which score.

The trade-off is that the HIP Score will never be a marketing-friendly badge that every product can earn with effort. It is meant to be a hard, methodology-driven number that means something specific. That is its credibility.

## Where to Go From Here

- The [methodology reference page](/methodology) for the full rubric, weights, and worked examples.
- The [Regenerative Index explainer](/blog/what-is-the-regenerative-index) for the most distinctive dimension of the seven.
- The [generic-vs-verified explainer](/blog/generic-vs-verified-ratings) for the headroom story.
- The [ratings catalogue](/ratings) for every category we have rated.

If you are a manufacturer interested in submitting evidence to lift a category-default rating into a verified rating, see [`/submit`](/submit).


---

*Methodology and edits by Chris Bowness; assistive AI used for drafting.*
