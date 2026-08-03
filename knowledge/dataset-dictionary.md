---
title: Dataset Dictionary
document_type: dataset_dictionary
department: analytics
region: global
version: "1.0"
effective_date: "2026-08-03"
access_level: public_demo
source: repository
---

# Dataset Dictionary

This dictionary defines the source datasets available to the business data analyst chatbot.

The dataset names, column names, metrics, and dimensions must match the Supabase Postgres contract used by the n8n workflow.

## Dataset: `ecommerce_orders`

Purpose: analyze ecommerce order transactions, product performance, channel performance, delivery, ratings, geography, and returns.

Grain: one row per ecommerce order line or order record in the sample dataset.

Date column: `order_date`

### Columns

| Column | Type | Role |
|---|---|---|
| `order_id` | Text | Identifier |
| `order_date` | Date | Date filter |
| `customer_id` | Text | Identifier |
| `customer_name` | Text | Descriptive field |
| `age_group` | Text | Dimension |
| `gender` | Text | Dimension |
| `region` | Text | Dimension |
| `country` | Text | Dimension |
| `city` | Text | Dimension |
| `product_category` | Text | Dimension |
| `product_name` | Text | Dimension |
| `sales_channel` | Text | Dimension |
| `quantity` | Numeric | Metric input |
| `unit_price` | Numeric | Metric input |
| `discount_percent` | Numeric | Metric input |
| `shipping_cost` | Numeric | Descriptive or future metric input |
| `payment_method` | Text | Dimension |
| `order_status` | Text | Dimension and metric input |
| `delivery_days` | Numeric | Metric input |
| `rating` | Numeric | Metric input |

### Supported Dimensions

- `product_category`
- `product_name`
- `region`
- `country`
- `city`
- `sales_channel`
- `payment_method`
- `order_status`
- `gender`
- `age_group`

### Known Product Categories

- Electronics
- Home & Kitchen
- Fashion
- Beauty
- Sports

### Common User Language

| User language | Schema mapping |
|---|---|
| product category, category, department | `product_category` |
| item, product | `product_name` |
| channel, sales channel, purchase channel | `sales_channel` |
| location, geography, market area | `region`, `country`, or `city` depending on wording |
| delivery speed, shipping time | `average_delivery_days` |
| customer score, review score | `average_rating` |
| returns, returned orders | `return_rate` or `order_status` |

### Supported Question Patterns

- highest or lowest metric by dimension
- breakdown of metric by dimension
- metric for a specific dimension value
- comparison of two or more dimension values
- date-filtered versions of the above

### Unsupported Ecommerce Boundaries

- profit or margin unless a future table includes product cost
- inventory, stockouts, fulfillment capacity, or warehouse operations
- customer lifetime value, cohorts, or repeat purchase behavior
- employee, payroll, or HR analytics

## Dataset: `marketing_campaigns`

Purpose: analyze marketing campaign performance across channels, devices, regions, audiences, objectives, and campaign status.

Grain: one row per marketing campaign performance record.

Date column: `campaign_date`

### Columns

| Column | Type | Role |
|---|---|---|
| `campaign_id` | Text | Identifier |
| `campaign_name` | Text | Descriptive field |
| `campaign_date` | Date | Date filter |
| `channel` | Text | Dimension |
| `region` | Text | Dimension |
| `country` | Text | Dimension |
| `audience_segment` | Text | Dimension |
| `device` | Text | Dimension |
| `campaign_objective` | Text | Dimension |
| `campaign_status` | Text | Dimension |
| `spend` | Numeric | Metric input |
| `impressions` | Numeric | Metric input |
| `clicks` | Numeric | Metric input |
| `conversions` | Numeric | Metric input |
| `revenue` | Numeric | Metric input |
| `leads` | Numeric | Metric input |
| `new_customers` | Numeric | Metric input |

### Supported Dimensions

- `channel`
- `region`
- `country`
- `audience_segment`
- `device`
- `campaign_objective`
- `campaign_status`

### Known Channels

- Display Ads
- Email
- Facebook
- Google Search
- Instagram
- LinkedIn
- TikTok
- YouTube

### Common User Language

| User language | Schema mapping |
|---|---|
| channel, marketing channel, platform, ad platform, source | `channel` |
| device, device type | `device` |
| audience, segment, customer segment | `audience_segment` |
| campaign goal, objective | `campaign_objective` |
| active or paused campaigns | `campaign_status` |
| ad return, return on ad spend, ROAS | `roas` |
| click through, click rate | `ctr` |
| conversion performance | `conversion_rate` |

### Supported Question Patterns

- highest or lowest metric by dimension
- breakdown of metric by dimension
- metric for a specific dimension value
- comparison of two or more dimension values
- date-filtered versions of the above

### Unsupported Marketing Boundaries

- organic social performance unless loaded into `marketing_campaigns`
- customer lifetime value or retention after acquisition
- attribution models beyond the revenue column in the source table
- creative-level or keyword-level analysis unless future fields are added

## Cross-Dataset Boundary

The current analytics workflow answers one dataset at a time.

Questions that require joining ecommerce and marketing should be handled as a future enhancement unless a controlled, documented join key is added.
