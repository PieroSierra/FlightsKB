---
kb_id: hack-booking-window-2024
type: hack
title: "Optimal Booking Window for Transatlantic Flights"
created: 2024-01-15
updated: 2024-01-15
status: reviewed
source:
  kind: internal
  name: PM Team
  url: null
  retrieved: null
confidence: high
tags: [booking, timing, transatlantic]
entities:
  routes: ["LHR-JFK", "LHR-LAX", "CDG-JFK"]
  cabins: [business, premium_economy]
---

## Rule of thumb: LHR to JFK best booking window

**Claim type:** rule_of_thumb
**Applies to:** routes=LHR-JFK
**Summary:** Best booking window tends to be 20-30 days before departure for business class.

Based on historical pricing analysis, business class fares on the LHR-JFK route typically reach their lowest point approximately 3-4 weeks before departure. This is when airlines begin adjusting inventory to ensure high load factors.

**Evidence:** Internal ML curve model; aggregated historical pricing from 2023
**Confidence:** high

## Warning: Peak season exceptions

**Claim type:** warning
**Applies to:** routes=LHR-JFK, routes=LHR-LAX
**Summary:** Peak seasons (July-August, Christmas) require earlier booking.

During peak travel seasons, the optimal booking window shifts to 45-60 days in advance. Last-minute availability is extremely limited and premiums can exceed 200% of off-peak pricing.

## Premium Economy sweet spot

**Claim type:** tactic
**Applies to:** cabin=premium_economy
**Summary:** Premium economy is best booked 6-8 weeks out for value.

Premium economy inventory is often more restricted than business class. Airlines tend to release PE seats in waves, with the best availability appearing 6-8 weeks before departure.
