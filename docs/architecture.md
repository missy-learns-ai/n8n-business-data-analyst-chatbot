# Architecture

## Current Workflow

The current project is an n8n business data analyst chatbot. It allows a user to ask natural-language business questions, retrieve data from connected Google Sheets, and receive a business-friendly answer in chat.

Current flow:

```text
Start Conversation
-> AI Agent
-> Google Sheets Tool(s)
-> Edit Fields
-> Chat Response
```

This is a strong proof of concept because it demonstrates that an AI agent can select a dataset, inspect spreadsheet data, and explain business findings. However, the current workflow gives the AI Agent too many responsibilities at once.

Phase 1 will refactor this into a more reliable analytical system where the language model plans and explains, while workflow nodes and deterministic code handle calculation, validation, routing, and logging.

## Current Node List

| Node | Type | Purpose |
|---|---|---|
| Start Conversation | Chat Trigger | Receives the user’s chat message and starts the workflow. |
| AI Agent | LangChain AI Agent | Interprets the question, selects tools, retrieves spreadsheet data, performs analysis, and writes the final response. |
| OpenAI Chat Model | OpenAI Chat Model | Provides the language model used by the AI Agent. |
| Simple Memory | Memory Buffer | Stores recent conversation context for follow-up questions. |
| E-commerce Orders & Customer Analysis | Google Sheets Tool | Gives the AI Agent access to ecommerce order data. |
| Marketing Campaign Performance Analysis | Google Sheets Tool | Gives the AI Agent access to marketing campaign performance data. |
| Edit Fields | Set Node | Converts the AI Agent `output` field into a cleaner `response` field. |
| Chat | Chat Response | Sends the final message back to the user. |
| Sticky Notes | n8n Documentation Notes | Explain the workflow visually inside the n8n canvas. |

## What Each Main Node Does

### Start Conversation

The Start Conversation node receives the user’s question through the n8n chat interface.

Recommended setting:

```text
Response Mode: Using Response Nodes
```

This setting allows the final Chat node to send the completed answer back to the user.

### AI Agent

The AI Agent is currently the central brain of the workflow. It is responsible for:

- understanding the user’s business question
- deciding which dataset is relevant
- selecting the right Google Sheets tool
- retrieving spreadsheet rows
- identifying relevant columns
- performing calculations
- writing the final business response

This is acceptable for a learning prototype, but it is risky for a real analytical system. The same model is currently responsible for both reasoning and calculation, which increases the chance of incorrect numbers, unsupported assumptions, or inconsistent answers.

### OpenAI Chat Model

The OpenAI Chat Model node provides the language model used by the AI Agent.

In the exported workflow, credentials are represented with placeholders. Real API keys and credential IDs should only be configured inside n8n credential storage and should never be committed to the repository.

### Simple Memory

The Simple Memory node stores recent conversation history. This allows the agent to understand follow-up questions such as:

```text
Now split that by region.
```

In Phase 1, memory should remain simple. More structured session memory can be added later in Phase 3.

### E-commerce Orders & Customer Analysis

This Google Sheets tool provides access to order-level ecommerce data.

The dataset includes fields such as:

- order ID
- order date
- customer information
- gender
- region
- product category
- product name
- sales channel
- quantity
- unit price
- discount percent
- shipping cost
- payment method
- order status
- delivery days
- rating

Example questions this dataset can answer:

- Which product category has the highest sales?
- How are PayPal orders distributed by gender?
- Which region has the highest return rate?
- What are the top 5 products by revenue?
- Which sales channel has the best average rating?

### Marketing Campaign Performance Analysis

This Google Sheets tool provides access to marketing campaign data.

The dataset includes fields such as:

- campaign ID
- campaign date
- campaign name
- channel
- region
- country
- audience segment
- device
- campaign objective
- spend
- impressions
- clicks
- conversions
- revenue
- leads
- new customers
- bounce rate
- average session duration
- campaign status

Example questions this dataset can answer:

- Which marketing channel has the highest ROAS?
- Which campaign generated the most revenue?
- Which audience segment has the best conversion rate?
- Are mobile campaigns performing better than desktop campaigns?
- Which campaigns have high spend but poor returns?

### Edit Fields

The Edit Fields node converts the AI Agent response into a cleaner field for the final chat response.

Current output field:

```text
output
```

Target response field:

```text
response
```

Recommended expression:

```text
{{ $json.output.replace(/\\n/g, '\n') }}
```

This helps convert escaped newline characters into actual line breaks.

### Chat

The Chat node sends the final response back to the user.

Recommended message value:

```text
{{ $json.response }}
```

The Chat node should return only the response text, not the full JSON object.

## Current Limitations

### 1. The AI Agent Does Too Much

The current AI Agent is responsible for planning, routing, retrieving, calculating, validating, and responding.

This makes the workflow harder to test and debug. If the answer is wrong, it is difficult to know whether the issue came from:

- bad dataset selection
- incorrect column interpretation
- calculation error
- missing data
- poor prompt behavior
- response formatting

Phase 1 should separate these responsibilities into clearer workflow steps.

### 2. Calculations Are Not Deterministic

The current workflow relies on the AI Agent to perform calculations directly from spreadsheet data.

This is risky because language models can make arithmetic mistakes or produce inconsistent results between runs.

In Phase 1, calculations should be performed by deterministic Code nodes or parameterized SQL. The model should explain verified results, not invent or recalculate numbers.

### 3. There Is No Structured Analysis Plan

The workflow does not currently produce a structured plan before executing the analysis.

A structured plan should include:

- user intent
- selected dataset
- metrics
- dimensions
- filters
- date range
- sorting or ranking instructions
- clarification status
- reason for dataset selection

Without this plan, it is hard to evaluate whether the agent selected the correct dataset or understood the question correctly.

### 4. Dataset Routing Is Prompt-Dependent

The AI Agent chooses between ecommerce and marketing tools based mostly on tool descriptions and prompt instructions.

This can work for simple questions, but routing should become more explicit and testable.

Phase 1 should introduce routing rules and a structured planner output so that dataset selection can be validated before analysis runs.

### 5. Data Quality Is Not Checked Explicitly

The current workflow does not include a dedicated data-quality validation step.

Phase 1 should check for:

- empty datasets
- missing required columns
- blank headers
- duplicate IDs
- invalid numeric values
- division by zero
- incomplete date periods
- missing date values
- unsupported filters

If a required dataset or column is missing, the workflow should fail safely instead of returning an unsupported answer.

### 6. Metric Definitions Are Not Centralized

Metric definitions currently live in documentation and prompts, but not in a machine-readable registry.

This creates a risk that different parts of the workflow may calculate the same metric differently.

Phase 1 should add a metric registry that defines each KPI once.

Example metrics:

| Metric | Dataset | Formula |
|---|---|---|
| Gross Sales | Ecommerce | `Quantity * Unit_Price` |
| Discount Amount | Ecommerce | `Gross Sales * Discount_Percent / 100` |
| Net Sales | Ecommerce | `Gross Sales - Discount Amount` |
| Estimated Profit | Ecommerce | `Net Sales * 0.35 - Shipping_Cost` |
| Return Rate | Ecommerce | `Returned Orders / Total Orders` |
| CTR | Marketing | `Clicks / Impressions` |
| Conversion Rate | Marketing | `Conversions / Clicks` |
| Cost per Click | Marketing | `Spend / Clicks` |
| Cost per Conversion | Marketing | `Spend / Conversions` |
| ROAS | Marketing | `Revenue / Spend` |
| Lead to Customer Rate | Marketing | `New_Customers / Leads` |

### 7. Responses Do Not Always Include Provenance

A reliable analytical answer should show where the result came from.

Phase 1 responses should consistently include:

- dataset name
- record count
- date period
- filters applied
- warnings, if relevant
- calculation method or metric definition

This helps users trust the answer and understand its limits.

### 8. There Is No Execution Logging

The current workflow does not store a structured execution record.

Phase 1 should log:

- trace ID
- timestamp
- user question
- selected dataset
- selected metrics
- row count
- date range
- warnings
- status
- latency
- error message, if any

This will make debugging much easier.

### 9. There Is No Regression Test Set

The repository does not yet include a formal set of test questions with expected results.

Phase 1 should add test questions for:

- dataset routing
- calculation accuracy
- date handling
- missing data
- ambiguous questions
- unsupported questions
- follow-up questions

This turns the project from a demo into something maintainable.

## Target Phase 1 Architecture

Phase 1 keeps a single orchestrator, but separates planning, validation, routing, calculation, data-quality checks, response generation, and logging.

Target flow:

```text
User / Chat UI
      |
Start Conversation
      |
Orchestrator Planner
      |
Structured Analysis Plan
      |
Plan Validation
      |
Dataset Router
      |
      +--> Ecommerce Analytics Workflow
      |
      +--> Marketing Analytics Workflow
      |
Deterministic Calculation Layer
      |
Data Quality Validation
      |
Response Composer
      |
Execution Logging
      |
Chat Response
```

## Target Phase 1 Components

| Component | Responsibility |
|---|---|
| Orchestrator Planner | Converts the user question into a structured analysis plan. |
| Plan Validation | Checks that the plan follows the required JSON schema. |
| Dataset Router | Routes the request to the correct analytics workflow. |
| Ecommerce Analytics Workflow | Handles ecommerce-specific retrieval, validation, and calculations. |
| Marketing Analytics Workflow | Handles marketing-specific retrieval, validation, and calculations. |
| Deterministic Calculation Layer | Calculates metrics using Code nodes or parameterized SQL. |
| Data Quality Validation | Checks dataset quality and produces warnings or controlled failures. |
| Response Composer | Converts verified results into a clear business response. |
| Execution Logging | Stores trace details for debugging and evaluation. |
| Error Handler | Returns safe failure messages when the workflow cannot answer reliably. |

## Recommended Phase 1 Workflow Files

The current single workflow should be split into separate importable n8n workflow files:

```text
workflows/
├── 01-orchestrator.json
├── 02-ecommerce-analytics.json
├── 03-marketing-analytics.json
└── 99-error-handler.json
```

### 01-orchestrator.json

Responsible for:

- receiving the user question
- generating the structured analysis plan
- validating the plan
- routing to the correct analytics workflow
- calling the response composer
- returning the final chat response

### 02-ecommerce-analytics.json

Responsible for:

- retrieving ecommerce data
- validating ecommerce columns
- calculating ecommerce metrics
- returning structured analytical results

### 03-marketing-analytics.json

Responsible for:

- retrieving marketing data
- validating marketing columns
- calculating marketing metrics
- returning structured analytical results

### 99-error-handler.json

Responsible for:

- returning safe failure messages
- formatting missing-data errors
- formatting unsupported-question errors
- logging failed executions

## Recommended Supporting Files

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
├── metric-registry.json
├── analytics-result.schema.json
└── warnings.schema.json

evaluations/
└── phase-1-test-questions.csv
```

## Structured Analysis Plan

The orchestrator should produce a structured analysis plan before any analytics workflow runs.

Example:

```json
{
  "intent": "compare",
  "dataset": "marketing",
  "metrics": ["spend", "revenue", "roas", "conversions"],
  "dimensions": ["device"],
  "filters": [],
  "date_range": {
    "start": "2025-01-02",
    "end": "2025-04-20"
  },
  "sort": null,
  "limit": null,
  "needs_clarification": false,
  "clarification_question": null,
  "routing_reason": "The question asks whether mobile campaigns perform better than desktop campaigns, which requires marketing campaign data grouped by device."
}
```

The analysis plan should be validated before execution. If the plan is invalid, the workflow should return a controlled failure message.

## Analytics Result Contract

Analytics workflows should return structured results instead of prose.

Example:

```json
{
  "trace_id": "phase1-20260730-001",
  "status": "success",
  "dataset": {
    "name": "Marketing Campaign Performance Analysis",
    "record_count": 80,
    "date_range": {
      "start": "2025-01-02",
      "end": "2025-04-20"
    }
  },
  "analysis": {
    "metric": "roas",
    "dimension": "channel",
    "results": [
      {
        "channel": "Google Search",
        "spend": 25000,
        "revenue": 92000,
        "roas": 3.68
      }
    ]
  },
  "warnings": [],
  "calculation_notes": [
    "ROAS calculated as Revenue / Spend."
  ]
}
```

The Response Composer should use this verified result to write the final answer. It should not recalculate the values.

## Data Quality Checks

Phase 1 should include basic validation before returning analytical answers.

Recommended checks:

| Check | Purpose |
|---|---|
| Empty dataset check | Prevents answers from being generated with no data. |
| Required column check | Confirms the calculation has the fields it needs. |
| Blank header check | Detects spreadsheet structure issues. |
| Duplicate ID check | Finds duplicated orders or campaigns. |
| Missing value check | Flags rows with missing required values. |
| Invalid denominator check | Prevents division by zero. |
| Date range check | Confirms the answer covers a known period. |
| Unsupported filter check | Prevents pretending a filter was applied when the column does not exist. |

Warnings should be included in the final answer when relevant.

## Response Requirements

Every Phase 1 answer should include:

- direct answer first
- supporting numbers
- dataset name
- record count
- date period
- warnings, if any
- short recommendation, if useful

The Response Composer should not invent new calculations. It should only explain the verified analytics result.

## Controlled Failure Rule

The workflow should not return an analytical answer when required data is unavailable.

Use this rule:

```text
No verified calculation result = no final analytical answer.
```

Examples of controlled failure messages:

```text
I cannot answer this reliably because the selected dataset does not contain a required `Revenue` column.
```

```text
I cannot calculate conversion rate because some rows have zero clicks, which would create an invalid denominator.
```

```text
I need a specific dataset to answer this. This project currently supports ecommerce orders and marketing campaign performance.
```

## Phase 1 Acceptance Criteria

Phase 1 is complete when:

- the agent selects the correct dataset for at least 90% of Phase 1 test questions
- all numerical answers match trusted reference calculations
- the workflow does not answer when required data is unavailable
- every answer includes dataset name, record count, date period, and warnings where relevant
- workflow JSON files contain no secrets or private credential values
- test questions are documented and repeatable
- repository documentation explains setup, architecture, and limitations

## Rationale

The purpose of Phase 1 is to turn the current prototype into a reliable analytical foundation.

The key architectural decision is:

```text
The language model should plan and explain.
Code or SQL should calculate.
Workflow nodes should validate and enforce the process.
```

This separation makes the system easier to test, easier to debug, and safer to use in real business scenarios.

Before changing the n8n workflow, this architecture document gives the project a clear map. That matters because n8n workflows can become difficult to reason about once many nodes are added. A written architecture helps keep the project organized as it grows from a simple chatbot into an agentic business intelligence platform.
