---
title: Ecommerce Analysis Playbook
document_type: playbook
department: ecommerce
region: global
version: "1.0"
effective_date: "2026-08-03"
access_level: public_demo
source: repository
---

# Ecommerce Analysis Playbook

This playbook provides guidance for interpreting ecommerce analytics results.

The analytics system should calculate numbers in Postgres and use this playbook only for interpretation, explanations, and follow-up suggestions.

## Common Ecommerce Questions

| Business question | Recommended metric | Recommended dimensions |
|---|---|---|
| Which category sells the most? | `net_sales` | `product_category` |
| Which channel has the most orders? | `order_count` | `sales_channel` |
| Which region has the highest sales? | `net_sales` | `region` |
| Which category has the highest return rate? | `return_rate` | `product_category` |
| Which city has the fastest delivery? | `average_delivery_days` | `city` |
| Which category has the best customer rating? | `average_rating` | `product_category` |

## Interpretation Guidance

### Net Sales

Use net sales as the default ecommerce revenue measure because it removes discounts from gross order value.

High net sales may be driven by order volume, unit price, or product mix. Do not claim which factor caused the result unless supporting data is retrieved or calculated.

### Order Count

Order count measures transaction volume. It is useful for demand and channel activity questions, but it does not measure revenue quality.

### Return Rate

Return rate measures the share of selected orders with `order_status = Returned`.

Higher return rate is usually a risk signal. It can indicate product fit, delivery issues, quality issues, or customer expectation gaps, but the chatbot must not claim a cause without supporting evidence.

### Average Rating

Average rating summarizes customer feedback. It should be interpreted together with record count because small groups may be noisy.

### Average Delivery Days

Lower average delivery days usually indicate faster fulfillment. If a question asks for the best delivery performance, sort this metric ascending.

## Recommended Warning Patterns

Disclose a warning when:

- the selected slice has zero records
- a requested category, channel, region, country, or city is not found
- the date period has no records
- the result depends on a small group compared with total row count
- date range fields are missing

## Follow-Up Suggestions

Useful follow-ups include:

- break the same metric down by another dimension
- compare two product categories or sales channels
- apply a date filter
- inspect return rate for a high-sales category
- inspect average rating for a high-return category

Follow-up suggestions should be short and should not imply that the system has already found a root cause.
