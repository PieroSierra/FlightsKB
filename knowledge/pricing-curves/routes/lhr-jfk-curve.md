---
kb_id: pricing-curve-lhr-jfk-2024
type: pricing_curve
title: "LHR-JFK Pricing Curve Analysis"
created: 2024-02-01
updated: 2024-02-01
status: reviewed
source:
  kind: internal
  name: ML Team
confidence: high
tags: [pricing, LHR, JFK, transatlantic]
entities:
  route: LHR-JFK
  carriers: [BA, AA, VS, DL]
---

## Price Curve Overview

**Claim type:** fact
**Applies to:** route=LHR-JFK
**Summary:** Business class prices typically decrease until 3-4 weeks out, then spike closer to departure.

Historical analysis shows LHR-JFK business class follows a predictable curve:
- 90+ days out: High launch fares
- 60-90 days: Gradual decrease
- 21-45 days: Lowest prices (sweet spot)
- 7-21 days: Prices begin rising
- 0-7 days: Significant premium

## Seasonal Variations

**Claim type:** rule_of_thumb
**Applies to:** route=LHR-JFK
**Summary:** Summer and Christmas periods show 30-50% premiums over baseline.

Peak periods (July-August, Dec 15-Jan 5) exhibit compressed curves with higher baseline prices. The sweet spot shifts earlier to 45-60 days for these periods.

## Carrier Comparison

**Claim type:** fact
**Applies to:** route=LHR-JFK
**Summary:** BA and AA price similarly; VS often 10-15% cheaper; DL via JFK connection can be competitive.

British Airways and American Airlines maintain price parity. Virgin Atlantic typically undercuts by 10-15% but has fewer frequencies. Delta connections via hubs can offer value.
