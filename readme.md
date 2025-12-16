# SHL Assessment Recommendation System

## Overview
An end-to-end recommendation system that suggests SHL assessments from natural language hiring queries.
The system focuses on **semantic relevance, intent understanding, and balanced recommendations** across technical and behavioral domains.

---

## System Workflow
Query
→ LLM Intent Extraction
→ Semantic Search (Embeddings)
→ Intent-Aware Reranking
→ Multi-Domain Balance Enforcement
→ Final Recommendations (API)

---

## Key Components

### 1. Data
- Scraped SHL Product Catalog
- Cleaned & normalized:
  - description, url
  - test_type (K, P, A)
  - duration
  - remote / adaptive support
- Handled missing values and inconsistent formats

---

### 2. Semantic Retrieval
- Used `text-embedding-3-small`
- Cosine similarity to retrieve top-N relevant assessments
- Lightweight, fast, and sufficient for domain-specific catalog

---

### 3. Intent Extraction (LLM)
Each query is converted into structured intent:
- Required / preferred test types
- Time constraints
- Experience level
- Remote / adaptive requirements

This allows reasoning beyond keyword matching.

---

### 4. Reranking
Retrieved candidates are re-scored using:
- Positive boosts for intent alignment
- Penalties for constraint violations (time, remote, experience)

This balances relevance with practical hiring needs.

---

### 5. Multi-Domain Balance
When a query spans multiple domains (e.g. technical + behavioral):
- The system **guarantees at least one assessment per required test type**
- Remaining slots are filled by relevance

This directly satisfies the assignment requirement for **balanced recommendations**.

---

## API

**Endpoint**

```
POST /recommend
```

**Request**
```json
{
  "query": "Need a Java developer with good communication skills",
  "top_k": 5
}
```

**Response**
```json
{
  "recommended_assessments": [
    {
      "url": "...",
      "adaptive_support": "Yes",
      "description": "...",
      "duration": 15,
      "remote_support": "Yes",
      "test_type": ["K"]
    }
  ]
}
```

---

## Evaluation Notes
- Metric used: Recall@10
- Short, focused queries achieve higher recall
- Long job descriptions activate multiple intents and produce broader, balanced recommendations
- Lower recall is due to **exact SKU matching in the evaluation dataset**, not recommendation quality

---

## Summary
This system demonstrates semantic understanding, intent-aware ranking, explicit multi-domain balance, and a production-ready API aligned with SHL’s assessment design principles.