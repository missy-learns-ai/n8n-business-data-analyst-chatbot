# n8n Business Data Analyst Chatbot

A chat-based AI business analyst workflow built in **n8n**.

This workflow allows users to ask natural-language business questions and receive clean, stakeholder-friendly analysis based on data stored in one or more connected **Google Sheets**.

The AI Agent dynamically chooses the most relevant Google Sheets dataset, retrieves the data, performs analysis, and responds in chat using a business-friendly Markdown format.

<img width="2670" height="1242" alt="Workflow overview" src="https://github.com/user-attachments/assets/63136991-fc8d-4bd8-bd0d-71eaf6c7fc5f" />


<img width="1394" height="795" alt="image" src="https://github.com/user-attachments/assets/aaab5729-a8c4-48b7-98b3-2dc1e508f456" />

---

## What This Workflow Does

This workflow turns Google Sheets into a simple conversational analytics layer.

Users can ask questions like:

- How are PayPal orders distributed between men and women?
- Which product category has the highest sales?
- Which marketing channel has the best ROAS?
- Which region has the highest return rate?
- What are the top-performing campaigns?
- Are mobile campaigns performing better than desktop campaigns?
- Which customer segment is generating the most revenue?

The workflow retrieves the relevant spreadsheet data, analyzes it, and returns a clear answer with metrics, insights, and recommendations.

---

## Workflow Overview

```text
When chat message received
        ↓
AI Agent
        ↓
Google Sheets Tool(s)
        ↓
Edit Fields
        ↓
Chat Response
```

---

## Main Components

### 1. Chat Trigger

The workflow starts when a user sends a message in the n8n chat interface.

Recommended setting:

```text
Response Mode: Using Response Nodes
```

This allows the final Chat node to send the formatted answer back to the user.

---

### 2. AI Agent

The AI Agent acts as the business data analyst.

It is responsible for:

- Understanding the user’s question
- Selecting the correct Google Sheets tool
- Retrieving the spreadsheet data
- Identifying relevant columns and metrics
- Performing calculations
- Returning a clear business answer

<img width="2846" height="1572" alt="AI Agent configuration" src="https://github.com/user-attachments/assets/96ba5685-8e50-43a8-b219-41b9fb3c54d3" />

Recommended AI Agent system prompt:

```text
You are a business data analyst.

You have access to one or more Google Sheets tools. Each tool may contain a different dataset.

For every user question:
1. Understand the business question and determine what type of data is needed.
2. Select the most relevant Google Sheets tool or tools based on the user’s question and the tool descriptions.
3. Retrieve the data before answering.
4. Analyze only the retrieved spreadsheet data.
5. Dynamically identify the relevant columns, metrics, filters, and groupings.
6. Perform calculations such as totals, averages, counts, percentages, rankings, comparisons, trends, correlations, and summaries where relevant.
7. If multiple datasets are needed, combine insights logically using matching columns if available.
8. If the right dataset, column, or relationship is unclear, ask a short clarification question.
9. If the data is missing or insufficient, clearly explain what is missing.

Do not invent data.
Do not answer from memory.
Do not assume a specific sheet structure.
Do not mention workflow or tool details unless the user asks.

Return a clear business-friendly answer in a top-down communication fashion. Top-down means that you start with your key point first, then provide supporting arguments.

Return the answer as clean Markdown for a chat user with numbers, insights, and recommendations where useful.

Do not return JSON.
Do not include escaped newline characters.
Do not end with a follow-up question unless the user explicitly asks for one.
```

---

### 3. Google Sheets Tool Nodes

Each Google Sheets node is connected to the AI Agent as a tool.

Each tool represents a dataset, such as:

- E-commerce orders
- Marketing campaign performance
- Customer support tickets
- Sales pipeline
- Inventory data

<img width="2876" height="1628" alt="Google Sheets tool configuration" src="https://github.com/user-attachments/assets/7bdb0967-fc66-4aab-9853-986d68e921c9" />

Example Google Sheets tool description for an e-commerce dataset:

```text
Use this tool to retrieve order-level e-commerce sales data, including customer, gender, payment method, product category, quantity, price, region, order status, and rating.
```

Example Google Sheets tool description for a marketing dataset:

```text
Use this tool to retrieve marketing campaign performance data, including campaign name, channel, region, country, audience segment, device, spend, impressions, clicks, conversions, revenue, leads, and new customers.
```

The AI Agent uses these descriptions to decide which dataset to retrieve for each user question.

---

### 4. Edit Fields Node

The AI Agent returns its response inside an `output` field.

The Edit Fields node maps that field into a cleaner `response` field for the final chat response.

Recommended field configuration:

```text
Field name: response
Field value: {{ $json.output.replace(/\\n/g, '\n') }}
Include Other Input Fields: OFF
```

This helps ensure that the final chat response receives only the formatted answer text.

---

### 5. Chat Response Node

The final Chat node sends the formatted response back to the user.

Recommended message value:

```text
{{ $json.response }}
```

Do not return the full JSON object.

Incorrect:

```text
{{ $json }}
```

Correct:

```text
{{ $json.response }}
```

---

## Repository Structure

Recommended project structure:

```text
n8n-business-data-analyst-chatbot/
├── README.md
├── workflow.template.json
├── .gitignore
├── sample-data/
│   ├── ecommerce-orders.csv
│   └── marketing-campaign-performance.csv
└── screenshots/
    ├── workflow-overview.png
    ├── ai-agent-config.png
    ├── google-sheets-tool-config.png
    └── chat-response-example.png
```

---

## Setup Instructions

### 1. Clone or Download This Repository

```bash
git clone https://github.com/YOUR_USERNAME/n8n-business-data-analyst-chatbot.git
cd n8n-business-data-analyst-chatbot
```

Or download the repository as a ZIP file from GitHub.

---

### 2. Import the Workflow into n8n

1. Open n8n.
2. Go to **Workflows**.
3. Click **Import from File**.
4. Select `workflow.template.json`.
5. Open the imported workflow.

---

### 3. Configure Your OpenAI Credential

This workflow uses an OpenAI Chat Model node.

In n8n:

1. Open the **OpenAI Chat Model** node.
2. Create or select your OpenAI credential.
3. Add your OpenAI API key in n8n’s credential manager.
4. Save the credential.

The public workflow template uses placeholders and does not include a real API key.

---

### 4. Configure Your Google Sheets Credential

In n8n:

1. Open each **Google Sheets Tool** node.
2. Create or select your Google Sheets OAuth2 credential.
3. Connect your Google account.
4. Select the Google Sheet document and sheet tab you want to use.
5. Save the node.

---

### 5. Replace Placeholder Values

The public workflow file contains placeholder values that must be replaced with your own n8n credentials and Google Sheet IDs.

Search the workflow file for placeholders such as:

```text
YOUR_OPENAI_CREDENTIAL_ID
YOUR_OPENAI_CREDENTIAL_NAME
YOUR_GOOGLE_SHEETS_CREDENTIAL_ID
YOUR_GOOGLE_SHEETS_CREDENTIAL_NAME
YOUR_ECOMMERCE_GOOGLE_SHEET_ID
YOUR_MARKETING_GOOGLE_SHEET_ID
YOUR_ECOMMERCE_GOOGLE_SHEET_URL
YOUR_MARKETING_GOOGLE_SHEET_URL
YOUR_CHAT_TRIGGER_WEBHOOK_ID
YOUR_CHAT_RESPONSE_WEBHOOK_ID
YOUR_N8N_INSTANCE_ID
YOUR_WORKFLOW_ID
YOUR_WORKFLOW_VERSION_ID
```

Replace them with values from your own n8n environment.

---

## Important Security Disclaimer

This repository is intended to provide a reusable workflow template.

The workflow file in this repository should **not** contain any real API keys, OAuth tokens, refresh tokens, access tokens, private webhook URLs, private Google Sheet links, or personal credentials.

Before publishing or sharing your own version of this workflow, carefully inspect your exported n8n workflow JSON file and remove or replace any sensitive values.

### Do Not Commit These Values

Never commit any of the following to GitHub:

- OpenAI API keys
- Google OAuth access tokens
- Google OAuth refresh tokens
- OAuth client secrets
- Private Google Sheet URLs
- Private Google Sheet document IDs
- Production webhook URLs
- n8n instance IDs
- Personal email addresses
- Internal company data
- Customer data
- Credential IDs from your private n8n instance

### Use Placeholders Instead

Use placeholders in your public workflow template.

Example OpenAI credential placeholder:

```json
{
  "credentials": {
    "openAiApi": {
      "id": "YOUR_OPENAI_CREDENTIAL_ID",
      "name": "YOUR_OPENAI_CREDENTIAL_NAME"
    }
  }
}
```

Example Google Sheet placeholder:

```json
{
  "documentId": {
    "__rl": true,
    "value": "YOUR_GOOGLE_SHEET_ID",
    "mode": "list",
    "cachedResultName": "YOUR_GOOGLE_SHEET_NAME",
    "cachedResultUrl": "YOUR_GOOGLE_SHEET_URL"
  }
}
```

Each user should replace these placeholders with their own credentials and sheet information after importing the workflow into n8n.

---

## If You Accidentally Commit a Secret

If you accidentally upload an API key, token, credential, or private sheet link to GitHub:

1. **Revoke or rotate the exposed secret immediately.**
2. Delete the secret from the repository.
3. Remove the secret from Git history if necessary.
4. Generate a new API key or OAuth credential.
5. Update your n8n credential with the new secret.

Deleting a file from GitHub is not always enough because secrets may remain in Git history.

---

## Sample Datasets

This repository includes sample datasets that can be copied into Google Sheets.

### E-commerce Orders Dataset

Useful for analyzing:

- Sales by product category
- Order distribution by gender
- Revenue by region
- Return rate by category
- Payment method usage
- Delivery performance
- Customer ratings

Example questions:

- Which product category has the highest sales?
- How are PayPal orders distributed by gender?
- Which region has the highest return rate?
- What are the top 5 products by revenue?
- Which sales channel has the best average rating?

---

### Marketing Campaign Performance Dataset

Useful for analyzing:

- ROAS
- CTR
- Conversion rate
- Cost per conversion
- Channel performance
- Audience performance
- Device performance
- Regional marketing performance

Example questions:

- Which marketing channel has the highest ROAS?
- Which campaign generated the most revenue?
- Which audience segment has the best conversion rate?
- Are mobile campaigns performing better than desktop campaigns?
- Which campaigns have high spend but poor returns?

---

## Recommended Calculated Metrics

For the e-commerce dataset:

```text
Gross Sales = Quantity * Unit Price
Discount Amount = Gross Sales * Discount %
Net Sales = Gross Sales - Discount Amount
Estimated Profit = Net Sales * 0.35 - Shipping Cost
Return Rate = Returned Orders / Total Orders
```

For the marketing dataset:

```text
CTR = Clicks / Impressions
Conversion Rate = Conversions / Clicks
Cost per Click = Spend / Clicks
Cost per Conversion = Spend / Conversions
ROAS = Revenue / Spend
Revenue per Click = Revenue / Clicks
Lead to Customer Rate = New Customers / Leads
```

---

## Example Chat Output

User question:

```text
How does the distribution of orders look between men and women using PayPal?
```

Example response:

```markdown
## PayPal orders are more common among women

Women placed 19 PayPal orders, compared with 6 PayPal orders from men.

| Gender | PayPal Orders | Share of PayPal Orders |
|---|---:|---:|
| Women | 19 | 76% |
| Men | 6 | 24% |

**Key insight:** Women account for about three out of every four PayPal orders in this dataset.

**Recommendation:** Review PayPal usage by product category and region to understand where this behavior is strongest.
```

---

## Common Issues and Fixes

### Chat Shows Raw JSON

**Problem**

The chat displays something like:

```json
[
  {
    "response": "..."
  }
]
```

**Cause**

The final Chat node is returning the full JSON object.

**Fix**

Use:

```text
{{ $json.response }}
```

Do not use:

```text
{{ $json }}
```

---

### Chat Trigger Shows a Response Mode Error

**Problem**

n8n says the chat trigger must use response nodes.

**Fix**

Open the **When chat message received** node and set:

```text
Response Mode: Using Response Nodes
```

---

### Final Chat Node Waits for Input

**Problem**

The final Chat node says it is waiting for user input.

**Cause**

The node is using a “Send and Wait for Response” operation.

**Fix**

Use a normal final response operation instead. The final Chat node should send the response and end the workflow.

---

### Google Sheets Data Is Not Retrieved

**Possible causes**

- Google Sheets credential is not configured.
- The wrong spreadsheet or tab is selected.
- The Google Sheets node is not connected as an AI tool.
- The tool description is too vague.
- The AI Agent prompt does not clearly instruct the agent to retrieve data before answering.

**Fixes**

- Reconnect Google Sheets credentials.
- Confirm the correct document and sheet tab.
- Improve the tool description.
- Make sure the AI Agent is connected to the Google Sheets node through the AI tool connection.
- Test the Google Sheets node independently.

---

### AI Agent Asks Too Many Clarification Questions

**Problem**

The agent asks for clarification even when the user question is reasonably answerable.

**Fix**

Use this instruction in the system prompt:

```text
If the user question is reasonably answerable from the available data, make a reasonable interpretation and proceed. Only ask a clarification question when the analysis cannot be performed without more information.
```

---

## Customizing the Workflow

You can add more Google Sheets tools for additional datasets.

Examples:

- Sales pipeline data
- Customer support tickets
- Product inventory
- Finance reports
- Customer satisfaction surveys
- Website analytics exports

For every new dataset:

1. Add a new Google Sheets Tool node.
2. Select the correct spreadsheet and sheet tab.
3. Write a clear tool description.
4. Connect the node to the AI Agent as an AI tool.

Example tool description:

```text
Use this tool to retrieve customer support ticket data, including ticket ID, date, customer segment, issue type, priority, status, resolution time, satisfaction score, and assigned team.
```

---

## Best Practices

- Keep the AI Agent system prompt dataset-agnostic.
- Put dataset-specific details in each Google Sheets tool description.
- Use clear column names in Google Sheets.
- Keep the first row as headers.
- Avoid merged cells in source sheets.
- Avoid blank header columns.
- Use consistent date formats.
- Use numeric fields for calculations.
- Do not publish real business or customer data.
- Use sample or anonymized datasets for public demos.

---

## Publishing Notes

Before publishing your workflow to GitHub:

- Export the workflow from n8n.
- Rename it to `workflow.template.json`.
- Replace private values with placeholders.
- Add sample datasets instead of private data.
- Add screenshots that do not reveal sensitive information.
- Review the workflow file manually before committing.

Recommended `.gitignore`:

```gitignore
.env
*.env
credentials.json
*.key
*.pem
.DS_Store
node_modules/
```

---

## License

Add your preferred license here.

Common options:

- MIT License
- Apache License 2.0
- GPLv3
- No license / All rights reserved

---

## Disclaimer

This workflow is provided as a learning and demonstration template.

You are responsible for configuring your own n8n credentials, API keys, Google Sheets access, data permissions, and security settings.

The workflow does not include real API keys or credentials. Any placeholders in the workflow must be replaced with your own values inside your private n8n environment.

Do not use this workflow with sensitive, confidential, regulated, or personally identifiable data unless your n8n instance, AI provider, and data handling processes meet your organization’s security and compliance requirements.
