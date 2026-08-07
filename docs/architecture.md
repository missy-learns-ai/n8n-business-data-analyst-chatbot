# Architecture

This document explains the current architecture of the Agentic Business Intelligence Chatbot.

The project is a production-inspired analytics agent built with n8n, Supabase Postgres, and Streamlit. The system lets users ask natural-language questions about ecommerce and marketing data while keeping calculations deterministic, auditable, and protected by guardrails.

## Core Design Principle

```text
The LLM plans and explains.
n8n validates, authorizes, routes, and logs.
Supabase Postgres calculates the numbers.
Streamlit provides the user-facing chat interface.
```

The language model does not calculate metrics directly, write raw SQL, choose unapproved tables, or execute database operations. It proposes a structured analysis plan. The workflow treats that plan as untrusted until deterministic guardrails approve it.

## High-Level Flow

```text
Streamlit UI
-> n8n Webhook
-> Request Guard
-> Prepare Input
-> Business Catalog
-> Planner / Cache
-> Validate Analysis Plan
-> Resolve Date Range
-> Fetch Dataset Metadata
-> Fetch Metric Definition
-> Metadata Authorization Guard
-> Build Analytics Query
-> SQL Safety Guard
-> Execute Analytics Query
-> Validate Analytics Result
-> Response Composer
-> Response Safety Guard
-> Format Final Response
-> Webhook Response
-> Execution Log
```

The importable workflow is stored at:

```text
workflows/business-data-analyst-chatbot.workflow.json
```

The older Google Sheets proof of concept is preserved separately:

```text
workflows/prototype-business-data-analyst-googlesheets.workflow.json
```

## Why The Workflow Was Refactored

The original proof of concept connected an AI agent directly to Google Sheets tools. That was useful for testing the user experience, but it had several problems:

- the AI agent handled planning, routing, retrieval, calculation, and response writing
- calculations were not fully deterministic
- dataset routing depended heavily on prompt instructions
- metric formulas were not enforced through a central source of truth
- data-quality checks were not explicit
- execution traces were not logged
- scaling to more datasets would require duplicated workflow logic

The current workflow uses Supabase Postgres and a metadata-driven execution layer. Instead of maintaining separate ecommerce and marketing query-builder branches, the workflow fetches approved dataset metadata and metric definitions, then builds deterministic SQL from those trusted components.

## Responsibility Split

| Component | Responsibility | Type |
|---|---|---|
| Streamlit UI | Provides the chat interface and calls the n8n webhook. | Application UI |
| Webhook | Receives user requests from Streamlit or another client. | n8n trigger |
| Request Guard | Validates request shape and blocks unsafe input before planner execution. | Deterministic guardrail |
| Prepare Input | Normalizes question, session, trace, and source-channel fields. | Deterministic |
| Business Catalog | Provides planner-facing dataset, metric, alias, and known-value context. | Deterministic context |
| Planner Agent | Converts the user question into a structured analysis plan. | AI |
| Planner Cache | Reuses previously validated unresolved plans for repeated questions. | Deterministic persistence |
| Validate Analysis Plan | Normalizes, canonicalizes, and validates planner or cached output. | Deterministic guardrail |
| Resolve Date Range | Converts relative periods such as last quarter into explicit dates. | Deterministic |
| Fetch Dataset Metadata | Reads approved dataset contract from Supabase. | Database lookup |
| Fetch Metric Definition | Reads approved metric formula and definition from Supabase. | Database lookup |
| Metadata Authorization Guard | Confirms selected metadata, metric, dimensions, filters, and date column are approved. | Deterministic guardrail |
| Build Analytics Query | Builds SQL from approved metadata, metric formulas, filters, and dates. | Deterministic |
| SQL Safety Guard | Blocks unsafe, destructive, unauthorized, or multi-statement SQL. | Deterministic guardrail |
| Execute Analytics Query | Runs the approved read-only query in Supabase Postgres. | Deterministic SQL |
| Validate Analytics Result | Checks empty results, missing values, warnings, and controlled failure cases. | Deterministic guardrail |
| Response Composer | Explains verified analytics JSON in concise business language. | AI |
| Response Safety Guard | Checks final text for missing source details, secrets, internals, or unsafe claims. | Deterministic guardrail |
| Execution Log | Stores trace data for success and controlled-failure paths. | Deterministic SQL |

## Metadata-Driven Analytics Engine

The workflow depends on two Supabase configuration tables.

### `dataset_metadata`

`dataset_metadata` defines which datasets are available and how they may be queried.

Important fields:

| Field | Purpose |
|---|---|
| `dataset_name` | Logical dataset key used by the planner. |
| `table_name` | Approved physical Postgres table. |
| `date_column` | Approved date column for date filters. |
| `dimensions` | JSON mapping of canonical dimension keys to SQL columns. |
| `dimension_aliases` | JSON mapping of user vocabulary to canonical dimensions. |
| `known_values` | Known dimension values used for planning and validation. |
| `supported_analysis_types` | Allowed deterministic analysis patterns. |
| `is_active` | Enables or disables dataset availability. |

The query builder does not accept table names or column names from the user or the model. It uses metadata that has already been authorized.

### `metric_registry`

`metric_registry` defines approved KPI formulas and business definitions.

Important fields:

| Field | Purpose |
|---|---|
| `metric_key` | Stable metric identifier such as `net_sales` or `roas`. |
| `dataset_name` | Dataset the metric belongs to. |
| `display_name` | Human-readable metric name. |
| `formula` | Trusted SQL snippet used inside controlled query templates. |
| `business_definition` | Plain-language meaning of the metric. |

Metric formulas are maintained by the project owner. End users must never be allowed to write or override formulas.

## Planner Contract

The Planner Agent returns structured JSON only. It does not answer the user and does not calculate values.

Example plan:

```json
{
  "route": "supported_analysis",
  "intent": "determine highest sales by product category",
  "dataset": "ecommerce_orders",
  "analysis_type": "grouped_metric_ranking",
  "metrics": ["net_sales"],
  "dimensions": ["product_category"],
  "filters": [],
  "date_range": {
    "start": null,
    "end": null,
    "date_column": "order_date",
    "relative_period": null
  },
  "limit": 1,
  "needs_clarification": false,
  "clarification_question": null
}
```

The validator then canonicalizes aliases, corrects safe dataset mismatches, infers missing dimensions from valid filters, and blocks invalid plans.

## Supported Routes

| Route | Meaning | Expected handling |
|---|---|---|
| `supported_analysis` | The question can be answered from approved analytics data. | Validate, authorize, build SQL, execute, validate result, compose answer. |
| `clarification` | The question is analytical but too vague. | Return one concise clarification question. |
| `unsupported` | The question is outside available datasets. | Return a controlled scope response. |
| `invalid_plan` | The planner or cached plan violates rules. | Return a safe failure response and log the issue. |
| `security_blocked` | Request guard detected unsafe input. | Return a controlled safety refusal and log security warnings. |

## Supported Analysis Types

| Analysis type | Use case |
|---|---|
| `total_summary` | One overall metric, such as total revenue or total orders. |
| `grouped_metric_ranking` | Highest, lowest, top, best, worst, most, or least by a dimension. |
| `grouped_metric_breakdown` | Breakdown of a metric by one dimension. |
| `filtered_grouped_breakdown` | Metric for a specific segment or filtered slice. |
| `dimension_comparison` | Compare two or more values in the same dimension. |

The planner can interpret flexible language, but the query builder only executes these approved patterns.

## Layered Guardrails

The workflow uses guardrails at every risky boundary.

| Guardrail | Placement | Purpose |
|---|---|---|
| Request Guard | Immediately after Webhook | Validates request shape, detects PII, prompt injection, secret extraction, and unsafe database intent before planner execution. |
| Cache Revalidation | Cache hit path before date resolution | Treats cached plans as untrusted and revalidates them through the same `Validate Analysis Plan` node as new planner outputs. |
| Validate Analysis Plan | After Planner Agent or cached plan restore | Normalizes planner output, applies aliases, validates dataset, metric, dimension, filters, date column, limit, and analysis type. |
| Metadata Authorization Guard | After dataset metadata and metric definition lookup | Confirms selected dataset, metric, dimensions, filters, table name, and date column are approved before SQL generation. |
| SQL Safety Guard | Between Build Analytics Query and Execute Analytics Query | Allows only read-only `SELECT` / `WITH` analytics queries and blocks destructive or multi-statement SQL patterns. |
| Validate Analytics Result | After Postgres execution | Checks empty results, missing values, invalid comparison values, null metric values, incomplete date ranges, warnings, and controlled failure cases. |
| Response Safety Guard | After Response Composer | Checks final user-facing text for empty responses, missing source details, internal implementation details, secrets, and unsafe claims. |
| Execution Log | Final logging path | Stores trace ID, question, selected dataset, metrics, analysis type, row count, date range, warnings, status, and timestamp. |

Security principles:

- User input is untrusted.
- Planner output is untrusted.
- Cached plans are untrusted.
- Metadata-driven context must be authorized before use.
- SQL is generated only from approved metadata and metric definitions.
- Postgres performs deterministic calculations.
- The LLM does not calculate metrics or execute SQL directly.
- Security warnings are logged internally.
- Data-quality warnings may be shown to users when helpful.

## Failure Routing

| Failure type | Route / status | User behavior |
|---|---|---|
| Prompt injection, PII, secret extraction, unsafe database intent | `security_blocked` | Controlled safety refusal |
| Out-of-scope but harmless request | `unsupported` | Scope explanation with suggested analytics topics |
| Ambiguous analytics request | `clarification` | One clarification question |
| Invalid planner output | `invalid_plan` | Safe failure message |
| Empty or incomplete analytics result | `failed` or `success_with_warnings` | Controlled response with data-quality warning |

Controlled failures should still return a stable JSON payload with a user-facing `response` field. This prevents empty webhook responses in Streamlit.

## Planner Cache Strategy

The planner cache stores unresolved structured plans, not final answers or SQL.

The cache should not store:

- generated SQL
- metric formulas
- final natural-language responses
- resolved relative dates
- raw database results

Relative date questions stay reusable because cached plans store values such as:

```json
{
  "relative_period": "last_quarter",
  "start": null,
  "end": null
}
```

The workflow resolves the actual date range at runtime. Cached plans still go through `Validate Analysis Plan`, so old cache entries cannot bypass new validation rules.

## SQL Generation Strategy

The query builder creates SQL from trusted components:

- approved table name from `dataset_metadata`
- approved date column from `dataset_metadata`
- approved dimension column from `dataset_metadata.dimensions`
- approved formula from `metric_registry`
- validated filters from the analysis plan
- resolved date range from `Resolve Date Range`

The model never writes SQL directly.

The SQL Safety Guard performs a final check before execution. It should block:

- undefined or empty SQL
- non-read-only SQL
- destructive statements such as `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `GRANT`, or `REVOKE`
- multi-statement SQL
- unauthorized table names
- suspicious comments or bypass patterns

## Database Permission Model

The workflow is designed to use separate database credentials.

| Credential | Used by | Permission intent |
|---|---|---|
| Supabase analytics reader | Metadata lookup, metric lookup, analytics query execution | Read-only access to approved analytics and metadata tables. |
| Supabase audit writer | Planner cache and execution log nodes | Write access only to audit/cache tables. |

The n8n workflow should not use the Supabase owner, service role, or full `postgres` credential for normal execution.

Recommended credential mapping:

| n8n node | Credential |
|---|---|
| `Fetch Dataset Metadata` | Analytics reader |
| `Fetch Metric Definition` | Analytics reader |
| `Execute Analytics Query` | Analytics reader |
| `Lookup Planner Cache` | Audit writer |
| `Save Planner Cache` | Audit writer |
| `Add Execution Log` | Audit writer |

## Analytics Result Contract

Analytics execution returns structured JSON, not prose.

Example shape:

```json
{
  "status": "success",
  "response_type": "analytics_result",
  "dataset": "ecommerce_orders",
  "analysis_type": "grouped_metric_ranking",
  "metrics": ["net_sales"],
  "dimensions": ["product_category"],
  "row_count": 1005,
  "date_start": "2025-01-01",
  "date_end": "2026-06-30",
  "warnings": [],
  "results": [
    {
      "dimension_value": "Electronics",
      "metric_value": "29296.07",
      "group_record_count": "223"
    }
  ]
}
```

The Response Composer may explain this verified payload, but must not recalculate or invent additional values.

## Response Requirements

Every successful analytics response should include:

- direct answer first
- verified metric value
- dataset name
- record count
- date range
- warnings, if any

The Response Composer should not mention SQL, workflow nodes, credentials, raw payloads, or internal implementation details. The Response Safety Guard checks this before the final response is returned.

## Execution Logging

The execution log records both success and controlled-failure paths.

Recommended fields:

| Field | Purpose |
|---|---|
| `trace_id` | Correlates a user request across workflow nodes. |
| `created_at` | Records when the execution happened. |
| `user_question` | Preserves the original user request for evaluation. |
| `selected_dataset` | Records ecommerce, marketing, or unknown. |
| `analysis_type` | Records the selected analysis pattern. |
| `metrics` | Records selected metrics as structured data. |
| `row_count` | Records how much data supported the answer. |
| `date_start` / `date_end` | Records the covered date period. |
| `warnings` | Records validation, data-quality, or security warnings. |
| `status` | Records success, warning, failure, unsupported, clarification, invalid plan, or security blocked. |

Execution logging makes the workflow auditable and gives the project a practical path for regression testing and future improvement.

## Repository Contracts

The repository should keep these contracts aligned with the live workflow:

| File | Purpose |
|---|---|
| `workflows/business-data-analyst-chatbot.workflow.json` | Sanitized importable n8n workflow. |
| `database/schema.sql` | Supabase table contract and seed metadata. |
| `docs/database-setup.md` | Human-readable database setup guide. |
| `schemas/analysis-plan.schema.json` | Planner structured output contract. |
| `schemas/metric-registry.json` | Repository-level metric registry reference. |
| `prompts/orchestrator-planner.md` | Planner prompt reference. |

Do not commit secrets, private webhook URLs, n8n credential IDs, model API keys, Supabase passwords, or private connection strings.

## Rationale

The workflow does not rely on the LLM to be correct or safe by itself.

Each risky boundary has a deterministic gate:

```text
The planner may propose.
The guards must verify.
The database must enforce.
The response must disclose.
```

This separation makes the system easier to test, easier to debug, safer to operate, and more realistic as a business data agent.
