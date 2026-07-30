# Architecture

This document records the baseline architecture for the original proof of concept and the target Phase 1 architecture for the reliable analytical foundation.

Phase 1 is currently being implemented on the `phase-1/reliable-analytics-foundation` branch. The live n8n workflow is still being refined and will be exported to the repository once the Phase 1 workflow is ready.

## Phase 1 Design Decision

The original prototype used Google Sheets as the analytical data source. Phase 1 now uses **Supabase Postgres** as the structured analytical store because real business datasets are expected to grow beyond the comfortable limits of a spreadsheet-backed chatbot.

The Phase 1 implementation keeps **one n8n orchestrator workflow** for now, but separates responsibility inside the workflow into clearly named zones:

```text
Chat Trigger
-> Prepare Input
-> Add Business Catalog
-> Planner Agent
-> Validate Analysis Plan
-> Main Switch
   -> ecommerce_orders analytics branch
   -> marketing_campaigns analytics branch
   -> clarification branch
   -> unsupported branch
   -> invalid_plan branch
-> Build Analytics Query / Controlled Response
-> Supabase Postgres deterministic query
-> Validate Analytics Result
-> Response Composer
-> Execution Log
-> Chat Response
```

This is a scope adjustment from the original specification, which proposed separate n8n workflow files for orchestrator, ecommerce analytics, marketing analytics and error handling. The current decision is to keep one workflow while the architecture is still changing quickly, then split into sub-workflows later only if the single workflow becomes difficult to maintain.

The important architectural separation is therefore **responsibility separation**, not necessarily file separation.

## Current Prototype Baseline

The repository still contains the original exported prototype workflow:

```text
business-data-analyst-chatbot.json
```

Original prototype flow:

```text
Start Conversation
-> AI Agent
-> Google Sheets Tool(s)
-> Edit Fields
-> Chat Response
```

The prototype demonstrates the basic user experience: a user asks a natural-language business question and receives a stakeholder-friendly analytical response. It is a useful proof of concept, but it is not yet reliable enough for real analytical use because the AI Agent handles too many responsibilities at once.

## Current Prototype Node Responsibilities

| Node | Type | Current responsibility |
|---|---|---|
| Start Conversation | Chat Trigger | Receives the user chat message and starts the workflow. |
| AI Agent | LangChain AI Agent | Interprets the question, selects Google Sheets tools, retrieves data, calculates values and writes the final response. |
| OpenAI Chat Model | OpenAI Chat Model | Provides the language model used by the AI Agent. |
| Simple Memory | Memory Buffer | Stores a small amount of recent conversation context. |
| E-commerce Orders & Customer Analysis | Google Sheets Tool | Provides access to ecommerce order data in the prototype. |
| Marketing Campaign Performance Analysis | Google Sheets Tool | Provides access to marketing campaign data in the prototype. |
| Edit Fields | Set node | Maps the AI Agent `output` field into a `response` field. |
| Chat | Chat Response | Sends the final message to the user. |
| Sticky Notes | Documentation notes | Explain the prototype workflow in the n8n canvas. |

## Prototype Limitations

### 1. The AI Agent Does Too Much

The original AI Agent is responsible for planning, routing, retrieving, calculating, validating and responding. If an answer is wrong, it is difficult to isolate whether the failure came from routing, data access, arithmetic, prompt behavior or response formatting.

### 2. Calculations Are Not Deterministic

The prototype allows the language model to calculate values directly from retrieved spreadsheet rows. That is risky because language models can make arithmetic mistakes or produce inconsistent answers between runs.

Phase 1 changes this rule:

```text
The model may plan and explain.
Supabase SQL calculates the numbers.
Workflow nodes validate and enforce the process.
```

### 3. Routing Is Prompt-Dependent

The prototype depends mostly on prompt instructions and tool descriptions for dataset routing. Phase 1 adds a structured analysis plan, a business catalog and a validator so routing can be tested.

### 4. Data Quality Is Not Explicitly Checked

The prototype does not have a dedicated validation step for empty results, missing required fields, duplicate IDs, invalid denominators, unsupported filters or incomplete date periods.

### 5. Metric Definitions Are Not Centralized

The prototype describes formulas in documentation, but does not enforce them through a machine-readable metric registry or a deterministic calculation layer.

### 6. Provenance Is Inconsistent

A reliable analytical answer should include the dataset, record count, date period and warnings where relevant. The prototype does not enforce this consistently.

### 7. Logging Is Missing

The prototype does not store a structured execution trace. Phase 1 adds execution logging so debugging and evaluation become possible.

## Target Phase 1 Architecture

```text
User / Chat UI
      |
Chat Trigger
      |
Prepare Input
      |
Add Business Catalog
      |
Planner Agent
      |
Structured Analysis Plan
      |
Validate Analysis Plan
      |
Main Switch
      |
      +-- clarification -> Build Controlled Response
      +-- unsupported -> Build Controlled Response
      +-- invalid_plan -> Build Controlled Response
      |
      +-- ecommerce_orders -> Build Analytics Query
      +-- marketing_campaigns -> Build Analytics Query
                              |
                        Supabase Postgres
                              |
                    Validate Analytics Result
                              |
                       Response Composer
                              |
                       Execution Logging
                              |
                         Chat Response
```

## Phase 1 Responsibility Zones

| Zone | Responsibility | Deterministic or AI? |
|---|---|---|
| Chat Trigger | Receives the user question. | Deterministic |
| Prepare Input | Normalizes the question, trace ID and workflow input fields. | Deterministic |
| Add Business Catalog | Provides the planner with allowed datasets, metrics and dimensions. | Deterministic |
| Planner Agent | Converts the user question into a structured analysis plan. | AI |
| Structured Output Parser | Forces the planner into the expected JSON shape. | Deterministic schema enforcement |
| Validate Analysis Plan | Checks route, dataset, metric, dimension, filter and date fields against the allowed catalog. | Deterministic |
| Main Switch | Routes supported, clarification, unsupported and invalid-plan requests. | Deterministic |
| Build Controlled Response | Returns safe messages for clarification, unsupported and invalid-plan cases. | Deterministic |
| Build Analytics Query | Converts a validated plan into an approved SQL query pattern. | Deterministic |
| Supabase Postgres | Stores ecommerce and marketing data and executes KPI calculations. | Deterministic SQL |
| Validate Analytics Result | Checks row count, null metrics, date period and warnings before a final answer is allowed. | Deterministic |
| Response Composer | Turns verified results into a top-down business response without recalculating values. | AI |
| Execution Logging | Stores trace ID, question, selected dataset, metrics, row count, warnings, latency and status. | Deterministic SQL |
| Chat Response | Sends only the final response text to the user. | Deterministic |

## Dataset Strategy

Phase 1 uses Supabase Postgres tables for structured analytics:

| Dataset | Table | Purpose |
|---|---|---|
| Ecommerce orders | `ecommerce_orders` | Order, customer, product, payment, return, delivery and rating analysis. |
| Marketing campaigns | `marketing_campaigns` | Campaign spend, revenue, ROAS, CTR, conversion, audience, channel and device analysis. |
| Metric registry | `metric_registry` or repository JSON contract | Defines KPI semantics and formulas. |
| Execution log | `analytics_execution_log` | Stores workflow trace and debugging information. |

SQL objects may be maintained directly in Supabase during Phase 1. The repository should still document any required table contracts, non-secret setup notes and workflow expectations so the project remains understandable and reproducible.

Do not commit Supabase passwords, private connection strings, credential IDs or private URLs.

## Planner Contract

The Planner Agent should return JSON only. Its job is to classify the user request and propose an analysis plan.

Expected fields:

```json
{
  "route": "supported_analysis",
  "intent": "rank",
  "dataset": "ecommerce_orders",
  "analysis_type": "grouped_metric_ranking",
  "metrics": ["net_sales"],
  "dimensions": ["product_category"],
  "filters": [],
  "date_range": {
    "start": null,
    "end": null,
    "date_column": "order_date"
  },
  "limit": 1,
  "needs_clarification": false,
  "clarification_question": null
}
```

The planner must not answer the business question, calculate metrics or write SQL.

## Supported Phase 1 Routes

| Route | Meaning | Expected handling |
|---|---|---|
| `supported_analysis` | The question can be answered from ecommerce or marketing data. | Validate and run deterministic analytics. |
| `clarification` | The question is analytical but too vague to choose dataset, metric or dimension. | Return one concise clarification question. |
| `unsupported` | The question is outside available datasets. | Return a controlled refusal. |
| `invalid_plan` | The planner produced a plan that violates catalog rules. | Return a safe failure message and log the issue. |

## Supported Initial Analysis Types

The target query layer should support generic analytical patterns rather than one branch per exact question.

| Analysis type | Use case |
|---|---|
| `total_summary` | One overall metric, such as total revenue or total orders. |
| `grouped_metric_ranking` | Highest, lowest, top, best, worst, most or least by a dimension. |
| `grouped_metric_breakdown` | Breakdown of a metric by one dimension. |
| `filtered_grouped_breakdown` | Detailed breakdown after applying one or more filters. |
| `dimension_comparison` | Compare two or more groups, such as mobile vs desktop. |

This design keeps the workflow scalable. The planner can interpret flexible language, while the query builder only executes approved patterns.

## Metric Registry Strategy

The project currently has a repository-level metric registry contract in:

```text
schemas/metric-registry.json
```

Phase 1 may also maintain the operational registry in Supabase. That is acceptable, but the contract must stay clear:

- metric IDs must be stable, such as `net_sales`, `return_rate`, `roas` and `conversion_rate`
- each metric belongs to exactly one dataset
- each metric lists required source fields
- ratio metrics must handle zero denominators safely
- formulas used in SQL must match trusted reference calculations

The workflow should avoid duplicated formulas over time. The long-term preference is to use the registry as the source of truth, either by reading from Supabase or by keeping the repository JSON and Supabase table synchronized.

## Analytics Result Contract

Analytics execution should return structured results instead of prose.

Example shape:

```json
{
  "status": "success",
  "dataset": "ecommerce_orders",
  "analysis_type": "grouped_metric_ranking",
  "metric": "net_sales",
  "dimension": "product_category",
  "record_count": 223,
  "date_start": "2025-01-01",
  "date_end": "2026-06-30",
  "warnings": [],
  "results": [
    {
      "dimension_value": "Electronics",
      "metric_value": 29296.07,
      "record_count": 223
    }
  ]
}
```

The Response Composer may explain this result, but must not recalculate or invent additional metrics.

## Data Quality Checks

Phase 1 should add validation before returning analytical answers.

| Check | Purpose |
|---|---|
| Empty result check | Prevents answers from being generated with no matching rows. |
| Required field check | Confirms the metric has the fields it needs. |
| Duplicate ID check | Finds duplicated orders or campaigns. |
| Missing value check | Flags missing required values. |
| Invalid denominator check | Prevents divide-by-zero metrics. |
| Date range check | Confirms the answer covers a known period. |
| Unsupported filter check | Prevents pretending a filter was applied when the field is not available. |
| Warning propagation | Ensures warnings reach the final response. |

## Response Requirements

Every successful Phase 1 response should include:

- direct answer first
- supporting numbers
- dataset name
- record count
- date period
- warnings, if any
- short recommendation, if useful

Controlled failure responses should not pretend an analytical result exists.

## Execution Logging Contract

The execution log should store enough information to debug and evaluate the workflow.

Recommended fields:

| Field | Purpose |
|---|---|
| `trace_id` | Correlates a user request across workflow nodes. |
| `created_at` | Records when the execution happened. |
| `user_question` | Preserves the original user request for evaluation. |
| `route` | Records supported, clarification, unsupported or invalid-plan handling. |
| `selected_dataset` | Records ecommerce, marketing or null. |
| `analysis_type` | Records the selected generic analysis pattern. |
| `metrics` | Records selected metrics as structured data. |
| `dimensions` | Records selected dimensions as structured data. |
| `row_count` | Records how much data supported the answer. |
| `date_start` / `date_end` | Records the covered date period. |
| `warnings` | Records validation warnings. |
| `status` | Records success or failure. |
| `latency_ms` | Supports performance debugging. |
| `error_message` | Captures controlled failures or unexpected errors. |

## Repository Documentation Expectations

P1-T01 is complete when the repository explains:

- the original prototype flow and its limitations
- the Supabase-backed Phase 1 target architecture
- the single-workflow responsibility-separation decision
- how the planner, validator, query builder, result validator, response composer and logger interact
- what must be exported once the n8n workflow is ready
- what must never be committed, including credentials and private connection strings

## Files Expected After Phase 1 Workflow Export

The workflow export is intentionally pending until the Phase 1 workflow is ready. Once ready, add:

```text
workflows/01-reliable-analytics-foundation.json
```

Supporting files expected over Phase 1:

```text
docs/
├── architecture.md
├── evaluation.md
└── operating-guide.md

prompts/
├── orchestrator-planner.md
└── response-composer.md

schemas/
├── analysis-plan.schema.json
├── dataset-dictionary.json
├── metric-registry.json
├── analytics-result.schema.json
└── warnings.schema.json

evaluations/
└── phase1-golden-questions.csv
```

## Phase 1 Acceptance Criteria

Phase 1 is complete when:

- the planner selects the correct dataset for at least 90% of Phase 1 test questions
- all numerical answers match trusted reference SQL calculations
- the workflow does not answer when required data is unavailable
- every successful answer includes dataset name, record count, date period and warnings where relevant
- workflow JSON files and repository files contain no secrets or private credential values
- test questions are documented and repeatable
- repository documentation explains setup, architecture and limitations

## Rationale

The purpose of Phase 1 is to turn the prototype into a reliable analytical foundation.

The key architectural rule is:

```text
The language model plans and explains.
Supabase SQL calculates.
Workflow nodes validate and enforce the process.
```

This separation makes the system easier to test, easier to debug and safer to use in real business scenarios.
