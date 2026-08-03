---
title: Marketing Analysis Playbook
document_type: playbook
department: marketing
region: global
version: "1.0"
effective_date: "2026-08-03"
access_level: public_demo
source: repository
---

# Marketing Analysis Playbook

This playbook provides guidance for interpreting marketing campaign analytics.

The analytics system should calculate numbers in Postgres and use this playbook only for interpretation, explanations, and follow-up suggestions.

## Common Marketing Questions

| Business question | Recommended metric | Recommended dimensions |
|---|---|---|
| Which channel has the highest ROAS? | `roas` | `channel` |
| Which channel has the highest spend? | `spend` | `channel` |
| Which device has the highest conversion rate? | `conversion_rate` | `device` |
| Which audience segment generated the most revenue? | `revenue` | `audience_segment` |
| Which campaign objective has the lowest cost per conversion? | `cost_per_conversion` | `campaign_objective` |
| Which region generated the most leads? | `leads` | `region` |

## Interpretation Guidance

### ROAS

ROAS measures revenue generated per dollar of spend. Higher ROAS usually means stronger revenue efficiency.

Do not treat ROAS as profit. It does not include cost of goods, operating cost, margin, or customer lifetime value.

### CTR

CTR measures how often impressions become clicks. It is useful for creative, audience, or channel engagement questions.

High CTR does not automatically mean high revenue or high conversion quality.

### Conversion Rate

Conversion rate measures how often clicks become conversions. It is useful for funnel-efficiency questions after the click.

### Cost Per Click

Cost per click measures paid media traffic cost. Lower values can be efficient, but they must be interpreted with click quality and conversion behavior.

### Cost Per Conversion

Cost per conversion measures spend needed to produce one conversion. Lower values are usually better, assuming conversion quality is comparable.

### Lead To Customer Rate

Lead to customer rate measures the share of leads that become new customers. It is useful when the question focuses on lead quality or downstream conversion.

## Recommended Warning Patterns

Disclose a warning when:

- requested channel values are not present in the dataset
- a ratio metric has a zero denominator
- a date period has no records
- a group has a very small record count
- a requested platform term must be mapped to `channel`

## Follow-Up Suggestions

Useful follow-ups include:

- compare ROAS and spend by channel
- inspect conversion rate by device
- compare revenue by audience segment
- apply a date filter such as last quarter or this year
- compare cost per conversion across campaign objectives

Follow-up suggestions should remain grounded in available metrics and dimensions.
