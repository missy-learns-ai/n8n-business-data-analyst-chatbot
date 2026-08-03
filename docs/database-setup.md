# Database Setup

This project uses Supabase Postgres as the analytics and logging layer.

The n8n workflow expects five tables:

- `ecommerce_orders`
- `marketing_campaigns`
- `metric_registry`
- `analytics_execution_log`
- `planner_cache`

Use [database/schema.sql](../database/schema.sql) as the reference schema.

---

## Source Tables

### `ecommerce_orders`

The ecommerce table stores order-level transaction data.

Required columns:

| Column | Type | Purpose |
|---|---|---|
| `order_id` | `text` | Order identifier |
| `order_date` | `date` | Date used for ecommerce date filters |
| `customer_id` | `text` | Customer identifier |
| `customer_name` | `text` | Customer display name |
| `age_group` | `text` | Customer age group |
| `gender` | `text` | Customer gender |
| `region` | `text` | Sales region |
| `country` | `text` | Sales country |
| `city` | `text` | Sales city |
| `product_category` | `text` | Product category |
| `product_name` | `text` | Product name |
| `sales_channel` | `text` | Order channel, such as Website or Mobile App |
| `quantity` | `numeric` | Quantity ordered |
| `unit_price` | `numeric` | Unit sales price |
| `discount_percent` | `numeric` | Discount percentage |
| `shipping_cost` | `numeric` | Shipping cost |
| `payment_method` | `text` | Payment method |
| `order_status` | `text` | Order status |
| `delivery_days` | `numeric` | Delivery duration in days |
| `rating` | `numeric` | Customer rating |

### `marketing_campaigns`

The marketing table stores campaign performance data.

Required columns:

| Column | Type | Purpose |
|---|---|---|
| `campaign_id` | `text` | Campaign identifier |
| `campaign_name` | `text` | Campaign display name |
| `campaign_date` | `date` | Date used for marketing date filters |
| `channel` | `text` | Marketing channel |
| `region` | `text` | Campaign region |
| `country` | `text` | Campaign country |
| `audience_segment` | `text` | Target audience segment |
| `device` | `text` | Device type |
| `campaign_objective` | `text` | Campaign objective |
| `campaign_status` | `text` | Campaign status |
| `spend` | `numeric` | Campaign spend |
| `impressions` | `numeric` | Ad impressions |
| `clicks` | `numeric` | Ad clicks |
| `conversions` | `numeric` | Campaign conversions |
| `revenue` | `numeric` | Attributed revenue |
| `leads` | `numeric` | Generated leads |
| `new_customers` | `numeric` | Acquired customers |

---

## Metric Registry

`metric_registry` stores the approved formulas used by the workflow query builders.

The workflow fetches one metric definition before building SQL:

```sql
SELECT
  metric_key,
  dataset_name,
  display_name,
  formula,
  business_definition
FROM metric_registry
WHERE dataset_name = '<dataset>'
  AND metric_key = '<metric>'
LIMIT 1;
```

Formula values must be trusted SQL snippets that are safe to place inside the workflow's controlled query templates.

Do not allow end users to write metric formulas directly.

---

## Execution Logging

`analytics_execution_log` stores traceability data for successful answers and controlled failures.

The workflow logs:

- `trace_id`
- `user_question`
- `selected_dataset`
- `metrics`
- `analysis_type`
- `row_count`
- `date_start`
- `date_end`
- `warnings`
- `status`
- `created_at`

This gives the project an audit trail for debugging, testing, and portfolio demonstrations.

---

## Planner Cache

`planner_cache` stores unresolved structured plans keyed by normalized question hash.

Relative dates should be cached unresolved. For example, a cached plan may store `relative_period = last_month` while leaving `start` and `end` empty. The workflow resolves the actual dates at runtime so cached relative questions remain correct over time.

---

## Importing Sample Data

The sample workbook archive is stored at:

[sample-data/business-data-analyst-sample-datasets.zip](../sample-data/business-data-analyst-sample-datasets.zip)

When uploading data into Supabase:

1. Extract the workbook archive.
2. Convert each workbook sheet to CSV if needed.
3. Create the tables using [database/schema.sql](../database/schema.sql).
4. Upload ecommerce rows into `ecommerce_orders`.
5. Upload marketing rows into `marketing_campaigns`.
6. Insert metric definitions into `metric_registry`.
7. Connect n8n Postgres nodes to the same Supabase database.

---

## Credential Handling

Do not commit Supabase connection strings, database passwords, or n8n credential IDs.

Keep private values in:

- Supabase project settings
- n8n credentials
- Streamlit secrets
- environment variables
