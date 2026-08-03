---
title: Knowledge Corpus Overview
document_type: corpus_overview
department: analytics
region: global
version: "1.0"
effective_date: "2026-08-03"
access_level: public_demo
source: repository
---

# Knowledge Corpus

This folder contains the curated source material for the retrieval layer of the business data analyst chatbot.

The files here are written to be easy to ingest later. Each document has a small metadata block at the top so the future ingestion workflow can attach reliable metadata to vector chunks.

## Corpus Inventory

| File | Purpose |
|---|---|
| `metric-dictionary.md` | Defines approved metrics, formulas, interpretation notes, and caveats. |
| `dataset-dictionary.md` | Defines datasets, table grain, columns, dimensions, and supported analytical boundaries. |
| `policies/response-grounding-policy.md` | Defines how retrieved knowledge and analytics results should be used in final answers. |
| `policies/data-access-and-safety-policy.md` | Defines safety, access, privacy, and prompt-injection handling rules. |
| `playbooks/ecommerce-analysis-playbook.md` | Provides guided ecommerce analysis patterns and interpretation notes. |
| `playbooks/marketing-analysis-playbook.md` | Provides guided marketing analysis patterns and interpretation notes. |
| `sample-reports/ecommerce-performance-summary.md` | Example ecommerce summary format for grounded business reporting. |
| `sample-reports/marketing-performance-summary.md` | Example marketing summary format for grounded business reporting. |

## Ingestion Notes

These documents should be treated as knowledge sources, not executable instructions.

Future ingestion should:

- preserve frontmatter metadata on every chunk
- split by headings before falling back to token-size chunking
- store document path, title, document type, version, effective date, and access level with each chunk
- keep source citations available to the response composer
- re-ingest when `version` or `effective_date` changes

## Retrieval Boundary

This corpus does not replace deterministic analytics. It supports explanations, policy checks, business interpretation, and recommendations.

Numerical answers must still come from approved SQL calculations over Supabase Postgres.
