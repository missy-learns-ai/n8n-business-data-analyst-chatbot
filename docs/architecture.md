# Architecture

## Current Workflow

The current project is an n8n business data analyst chatbot. It allows a user to ask natural-language business questions, retrieves data from Google Sheets, and returns a business-friendly answer in chat.

Current flow:

```text
Start Conversation
-> AI Agent
-> Google Sheets Tool(s)
-> Edit Fields
-> Chat Response

Current Node List
Node	Purpose
Start Conversation	Receives the user’s chat message and starts the workflow.
AI Agent	Interprets the question, chooses a Google Sheets tool, retrieves data, performs analysis, and writes the final answer.
OpenAI Chat Model	Provides the language model used by the AI Agent.
Simple Memory	Stores recent conversation context so the agent can respond to follow-up questions.
E-commerce Orders & Customer Analysis	Google Sheets tool for order-level ecommerce data.
Marketing Campaign Performance Analysis	Google Sheets tool for marketing campaign data.
Edit Fields	Converts the AI Agent output field into a cleaner response field.
Chat	Sends the final response back to the user.
Sticky Notes	Explain workflow behavior inside the n8n canvas.

What Each Main Node Does
Start Conversation
This is the chat trigger. It receives the user’s question and passes it into the workflow.
Recommended setting:
Response Mode: Using Response Nodes
This allows the final Chat node to send a clean response back to the user.
AI Agent
The AI Agent currently owns most of the workflow logic. It is responsible for:
understanding the user’s question
deciding which dataset is relevant
calling the correct Google Sheets tool
retrieving spreadsheet rows
identifying relevant columns
performing calculations
writing the final answer
This works for a prototype, but it is risky for a real analytical system because the model is both reasoning and calculating.
Google Sheets Tools
The workflow currently has two Google Sheets tools:
ecommerce orders and customer analysis
marketing campaign performance analysis
Each tool gives the AI Agent access to a different dataset.
The AI Agent chooses between them using the tool names, tool descriptions, and the user’s question.
Edit Fields
The AI Agent returns text in an output field. The Edit Fields node maps that value into a simpler response field.
Current expression:
{{ $json.output.replace(/\\n/g, '\n') }}
This helps prevent escaped newline characters from appearing in the final chat response.
Chat
The Chat node sends the final response back to the user.
Recommended message value:
{{ $json.response }}
Current Limitations
The current workflow is useful as a proof of concept, but it has several limitations.
1. The AI Agent Does Too Much
The same agent currently plans the analysis, retrieves data, calculates metrics, validates assumptions, and writes the final answer.
This creates reliability risk because language models can make calculation mistakes or skip validation steps.
2. Calculations Are Not Deterministic
Numerical analysis is currently performed by the AI Agent instead of a dedicated Code node or database query.
This means answers may vary between runs and may not always match trusted reference calculations.
3. There Is No Structured Analysis Plan
The workflow does not first produce a validated plan such as:
selected dataset
metric
dimension
filters
date range
required calculation
clarification status
Without a structured plan, it is harder to test routing accuracy or debug why the agent chose a specific dataset.
4. Data Quality Is Not Checked Explicitly
The workflow does not currently have a dedicated validation step for:
empty datasets
missing required columns
blank headers
duplicate IDs
invalid denominators
incomplete date periods
This matters because real business data is often messy.
5. Metric Definitions Are Only Prompt-Based
Metrics such as ROAS, conversion rate, net sales, and return rate are described in documentation, but they are not yet stored in a machine-readable metric registry.
This makes it harder to keep prompts, calculations, documentation, and tests aligned.
6. Responses Lack Consistent Provenance
The final answer may include useful analysis, but it does not consistently include:
dataset name
record count
date range
warnings
calculation method
Phase 1 should make these fields mandatory.
7. No Regression Test Set Exists Yet
There is no formal set of test questions and trusted expected answers.
Without tests, it is difficult to know whether future workflow changes improve or break the system.
Target Phase 1 Architecture
Phase 1 keeps a single orchestrator, but separates planning, routing, calculation, validation, and response composition.
Target flow:
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
Target Phase 1 Responsibilities
Component	Responsibility
Orchestrator Planner	Converts the user question into a structured analysis plan.
Plan Validation	Checks that the plan follows the expected schema.
Dataset Router	Sends the request to the correct analytics workflow.
Ecommerce Analytics Workflow	Handles ecommerce-specific calculations.
Marketing Analytics Workflow	Handles marketing-specific calculations.
Deterministic Calculation Layer	Uses Code nodes or parameterized SQL to calculate metrics.
Data Quality Validation	Checks source data and returns warnings or controlled failures.
Response Composer	Turns verified results into a clear business answer.
Execution Logging	Stores trace ID, question, dataset, row count, warnings, latency, and status.
Error Handler	Returns safe failure messages when the workflow cannot answer reliably.

Target Phase 1 Workflow Files
Recommended repository structure:
workflows/
├── 01-orchestrator.json
├── 02-ecommerce-analytics.json
├── 03-marketing-analytics.json
└── 99-error-handler.json
Supporting files:
docs/
└── architecture.md

prompts/
├── orchestrator-planner.md
└── response-composer.md

schemas/
├── analysis-plan.schema.json
├── metric-registry.json
└── warnings.schema.json

evaluations/
└── phase-1-test-questions.csv
Rationale
Before changing the workflow, the project needs a clear map of the current system and the target Phase 1 system.
This documentation helps prevent confusion inside the n8n visual editor. It also creates a shared reference for future decisions, testing, debugging, and portfolio presentation.
The main Phase 1 architectural decision is:
The language model should plan and explain.
Code or SQL should calculate.
Workflow nodes should validate and enforce the process.
