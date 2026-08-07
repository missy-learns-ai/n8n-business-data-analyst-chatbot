-- Supabase Postgres schema for the business data analyst chatbot.
-- Run this in the Supabase SQL editor before uploading source data.

create table if not exists ecommerce_orders (
  order_id text,
  order_date date,
  customer_id text,
  customer_name text,
  age_group text,
  gender text,
  region text,
  country text,
  city text,
  product_category text,
  product_name text,
  sales_channel text,
  quantity numeric,
  unit_price numeric,
  discount_percent numeric,
  shipping_cost numeric,
  payment_method text,
  order_status text,
  delivery_days numeric,
  rating numeric
);

create index if not exists idx_ecommerce_orders_order_date
  on ecommerce_orders (order_date);

create index if not exists idx_ecommerce_orders_product_category
  on ecommerce_orders (product_category);

create index if not exists idx_ecommerce_orders_sales_channel
  on ecommerce_orders (sales_channel);

create index if not exists idx_ecommerce_orders_region
  on ecommerce_orders (region);

create table if not exists marketing_campaigns (
  campaign_id text,
  campaign_name text,
  campaign_date date,
  channel text,
  region text,
  country text,
  audience_segment text,
  device text,
  campaign_objective text,
  campaign_status text,
  spend numeric,
  impressions numeric,
  clicks numeric,
  conversions numeric,
  revenue numeric,
  leads numeric,
  new_customers numeric
);

create index if not exists idx_marketing_campaigns_campaign_date
  on marketing_campaigns (campaign_date);

create index if not exists idx_marketing_campaigns_channel
  on marketing_campaigns (channel);

create index if not exists idx_marketing_campaigns_device
  on marketing_campaigns (device);

create index if not exists idx_marketing_campaigns_region
  on marketing_campaigns (region);

create table if not exists dataset_metadata (
  dataset_name text primary key,
  display_name text not null,
  description text not null,
  table_name text not null,
  date_column text not null,
  dimensions jsonb not null default '{}'::jsonb,
  dimension_aliases jsonb not null default '{}'::jsonb,
  known_values jsonb not null default '{}'::jsonb,
  supported_analysis_types jsonb not null default '[]'::jsonb,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

insert into dataset_metadata (
  dataset_name,
  display_name,
  description,
  table_name,
  date_column,
  dimensions,
  dimension_aliases,
  known_values,
  supported_analysis_types,
  is_active
)
values
  (
    'ecommerce_orders',
    'Ecommerce Orders',
    'Online ecommerce order transaction data.',
    'ecommerce_orders',
    'order_date',
    '{
      "gender": "gender",
      "region": "region",
      "country": "country",
      "city": "city",
      "product_category": "product_category",
      "product_name": "product_name",
      "sales_channel": "sales_channel",
      "payment_method": "payment_method",
      "order_status": "order_status",
      "age_group": "age_group"
    }'::jsonb,
    '{
      "category": "product_category",
      "product_category_name": "product_category",
      "product_type": "product_category",
      "item_category": "product_category",
      "product": "product_name",
      "item": "product_name",
      "channel": "sales_channel",
      "order_channel": "sales_channel",
      "purchase_channel": "sales_channel",
      "platform": "sales_channel",
      "payment": "payment_method",
      "status": "order_status",
      "location": "region",
      "market": "region",
      "geography": "region"
    }'::jsonb,
    '{
      "product_category": ["Electronics", "Home & Kitchen", "Fashion", "Beauty", "Sports"]
    }'::jsonb,
    '[
      "total_summary",
      "grouped_metric_ranking",
      "grouped_metric_breakdown",
      "filtered_grouped_breakdown",
      "dimension_comparison"
    ]'::jsonb,
    true
  ),
  (
    'marketing_campaigns',
    'Marketing Campaigns',
    'Marketing campaign performance data.',
    'marketing_campaigns',
    'campaign_date',
    '{
      "campaign_name": "campaign_name",
      "channel": "channel",
      "region": "region",
      "country": "country",
      "audience_segment": "audience_segment",
      "device": "device",
      "campaign_objective": "campaign_objective",
      "campaign_status": "campaign_status"
    }'::jsonb,
    '{
      "platform": "channel",
      "ad_platform": "channel",
      "marketing_platform": "channel",
      "social_platform": "channel",
      "marketing_channel": "channel",
      "campaign_channel": "channel",
      "traffic_channel": "channel",
      "traffic_source": "channel",
      "ad_channel": "channel",
      "source": "channel",
      "placement": "channel",
      "audience": "audience_segment",
      "segment": "audience_segment",
      "objective": "campaign_objective",
      "status": "campaign_status"
    }'::jsonb,
    '{
      "channel": ["Display Ads", "Email", "Facebook", "Google Search", "Instagram", "LinkedIn", "TikTok", "YouTube"]
    }'::jsonb,
    '[
      "total_summary",
      "grouped_metric_ranking",
      "grouped_metric_breakdown",
      "filtered_grouped_breakdown",
      "dimension_comparison"
    ]'::jsonb,
    true
  )
on conflict (dataset_name) do update set
  display_name = excluded.display_name,
  description = excluded.description,
  table_name = excluded.table_name,
  date_column = excluded.date_column,
  dimensions = excluded.dimensions,
  dimension_aliases = excluded.dimension_aliases,
  known_values = excluded.known_values,
  supported_analysis_types = excluded.supported_analysis_types,
  is_active = excluded.is_active,
  updated_at = now();

create table if not exists metric_registry (
  metric_key text primary key,
  dataset_name text not null,
  display_name text not null,
  formula text not null,
  business_definition text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

insert into metric_registry (
  metric_key,
  dataset_name,
  display_name,
  formula,
  business_definition
)
values
  (
    'order_count',
    'ecommerce_orders',
    'Order Count',
    'COUNT(*)',
    'Total number of ecommerce orders.'
  ),
  (
    'gross_sales',
    'ecommerce_orders',
    'Gross Sales',
    'SUM(quantity * unit_price)',
    'Total sales before discounts are removed.'
  ),
  (
    'net_sales',
    'ecommerce_orders',
    'Net Sales',
    'SUM((quantity * unit_price) - ((quantity * unit_price) * discount_percent / 100))',
    'Sales after discounts are removed.'
  ),
  (
    'return_rate',
    'ecommerce_orders',
    'Return Rate',
    'COUNT(*) FILTER (WHERE order_status = ''Returned'')::numeric / NULLIF(COUNT(*), 0)',
    'Share of orders with Returned status.'
  ),
  (
    'average_rating',
    'ecommerce_orders',
    'Average Rating',
    'AVG(rating)',
    'Average customer rating across ecommerce orders.'
  ),
  (
    'average_delivery_days',
    'ecommerce_orders',
    'Average Delivery Days',
    'AVG(delivery_days)',
    'Average number of days between order and delivery.'
  ),
  (
    'spend',
    'marketing_campaigns',
    'Spend',
    'SUM(spend)',
    'Total marketing campaign spend.'
  ),
  (
    'impressions',
    'marketing_campaigns',
    'Impressions',
    'SUM(impressions)',
    'Total number of ad impressions.'
  ),
  (
    'clicks',
    'marketing_campaigns',
    'Clicks',
    'SUM(clicks)',
    'Total number of ad clicks.'
  ),
  (
    'conversions',
    'marketing_campaigns',
    'Conversions',
    'SUM(conversions)',
    'Total number of campaign conversions.'
  ),
  (
    'revenue',
    'marketing_campaigns',
    'Revenue',
    'SUM(revenue)',
    'Total revenue attributed to marketing campaigns.'
  ),
  (
    'leads',
    'marketing_campaigns',
    'Leads',
    'SUM(leads)',
    'Total number of leads generated by marketing campaigns.'
  ),
  (
    'new_customers',
    'marketing_campaigns',
    'New Customers',
    'SUM(new_customers)',
    'Total number of new customers acquired through marketing campaigns.'
  ),
  (
    'ctr',
    'marketing_campaigns',
    'Click Through Rate',
    'SUM(clicks)::numeric / NULLIF(SUM(impressions), 0)',
    'Share of impressions that became clicks.'
  ),
  (
    'conversion_rate',
    'marketing_campaigns',
    'Conversion Rate',
    'SUM(conversions)::numeric / NULLIF(SUM(clicks), 0)',
    'Share of clicks that became conversions.'
  ),
  (
    'cost_per_click',
    'marketing_campaigns',
    'Cost Per Click',
    'SUM(spend)::numeric / NULLIF(SUM(clicks), 0)',
    'Average marketing spend per click.'
  ),
  (
    'cost_per_conversion',
    'marketing_campaigns',
    'Cost Per Conversion',
    'SUM(spend)::numeric / NULLIF(SUM(conversions), 0)',
    'Average marketing spend per conversion.'
  ),
  (
    'roas',
    'marketing_campaigns',
    'ROAS',
    'SUM(revenue)::numeric / NULLIF(SUM(spend), 0)',
    'Revenue generated per dollar of ad spend.'
  ),
  (
    'revenue_per_click',
    'marketing_campaigns',
    'Revenue Per Click',
    'SUM(revenue)::numeric / NULLIF(SUM(clicks), 0)',
    'Average revenue generated per click.'
  ),
  (
    'lead_to_customer_rate',
    'marketing_campaigns',
    'Lead To Customer Rate',
    'SUM(new_customers)::numeric / NULLIF(SUM(leads), 0)',
    'Share of leads that became new customers.'
  )
on conflict (metric_key) do update set
  dataset_name = excluded.dataset_name,
  display_name = excluded.display_name,
  formula = excluded.formula,
  business_definition = excluded.business_definition,
  updated_at = now();

create table if not exists analytics_execution_log (
  id bigserial primary key,
  trace_id text,
  user_question text,
  selected_dataset text,
  metrics jsonb not null default '[]'::jsonb,
  analysis_type text,
  row_count integer not null default 0,
  date_start date,
  date_end date,
  warnings jsonb not null default '[]'::jsonb,
  status text not null default 'unknown',
  created_at timestamptz not null default now()
);

create index if not exists idx_analytics_execution_log_trace_id
  on analytics_execution_log (trace_id);

create index if not exists idx_analytics_execution_log_created_at
  on analytics_execution_log (created_at desc);

create index if not exists idx_analytics_execution_log_status
  on analytics_execution_log (status);

create table if not exists planner_cache (
  question_hash text primary key,
  normalized_question text not null,
  catalog_version text not null,
  plan jsonb not null,
  route text,
  dataset text,
  analysis_type text,
  metrics jsonb not null default '[]'::jsonb,
  dimensions jsonb not null default '[]'::jsonb,
  hit_count integer not null default 0,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  last_used_at timestamptz not null default now()
);

create index if not exists idx_planner_cache_active
  on planner_cache (is_active);

create index if not exists idx_planner_cache_last_used_at
  on planner_cache (last_used_at desc);
