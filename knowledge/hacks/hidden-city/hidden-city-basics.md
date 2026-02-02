---
kb_id: hidden-city-2024
type: hack
title: "Hidden City Ticketing Explained"
created: 2024-01-28
updated: 2024-01-28
status: reviewed
source:
  kind: internal
  name: PM Team
confidence: medium
tags: [hidden-city, skiplagging, fares]
entities:
  type: fare-hack
---

## What is Hidden City Ticketing?

**Claim type:** fact
**Applies to:** type=fare-hack
**Summary:** Booking a flight with a connection and deplaning at the connection city instead of the final destination.

Hidden city ticketing exploits pricing anomalies where a flight A→B→C costs less than A→B directly. The passenger books to C but exits at B.

## Risks and Limitations

**Claim type:** warning
**Applies to:** type=fare-hack
**Summary:** Airlines prohibit this practice and may penalize frequent offenders.

Risks include:
- Checked bags will go to final destination
- Return flights will be cancelled if outbound is not completed
- Frequent flyer accounts may be terminated
- Only works one-way with carry-on only
