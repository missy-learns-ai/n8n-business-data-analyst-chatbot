---
title: Response Grounding Policy
document_type: policy
department: governance
region: global
version: "1.0"
effective_date: "2026-08-03"
access_level: public_demo
source: repository
---

# Response Grounding Policy

This policy defines how the chatbot should combine deterministic analytics results with retrieved business knowledge.

## Core Rule

Final answers must separate verified data from interpretation.

The model may explain and summarize, but it must not invent numbers, recalculate values, or make claims that are not supported by analytics output or retrieved documents.

## Recommended Response Structure

When both analytics and knowledge retrieval are used, answers should follow this structure:

1. Observation: what the verified data says.
2. Documented guidance: what the retrieved policy, playbook, or report says.
3. Recommendation: what action is reasonable based on both sources.
4. Warnings: missing data, incomplete periods, invalid denominators, unsupported filters, or unavailable comparison values.
5. Sources: dataset name, record count, date range, and retrieved document citations.

For short factual questions, the response may be shorter, but it must still include source details.

## Numeric Grounding Rules

- Use only numeric values from validated analytics results.
- Do not round beyond the value already provided by the analytics result.
- Do not compute percentage changes, ratios, rankings, or deltas in the response composer.
- If a required value is missing, return a controlled failure or warning.
- If a comparison value is unavailable, do not compare against it.

## Retrieval Grounding Rules

- Retrieved documents can support definitions, policies, interpretation, and recommended actions.
- Retrieved documents cannot override deterministic analytics results.
- If retrieval confidence is low or no relevant source is found, the response must avoid document-backed claims.
- Every recommendation must be traceable to at least one verified observation and one relevant retrieved source.

## Unsupported Claim Handling

The chatbot must not claim:

- causality from correlation
- future performance without a forecasting method
- financial impact beyond the calculated metric
- root cause without supporting data
- policy guidance that does not appear in retrieved knowledge

## Controlled Failure Rules

Return a controlled failure when:

- the requested dataset is unavailable
- the requested metric is not approved
- the requested dimension is not in the dataset dictionary
- the filtered dataset slice returns no usable records
- a ratio metric has an invalid denominator
- the question requires private, sensitive, or unsupported data
