# Business Knowledge Base Agent — Architecture

## Core pipeline

```text
Business documents
  ↓
Load text from file / folder / URL
  ↓
Split into chunks
  ↓
Create embeddings
  ↓
Store chunks + metadata + embeddings
  ↓
User asks question
  ↓
Embed question
  ↓
Retrieve relevant chunks
  ↓
Build grounded prompt
  ↓
Generate answer
  ↓
Validate answer
  ↓
Return answer + sources
```

## Current local architecture

```text
frontend/widget.html
        ↓ HTTP
FastAPI backend
        ↓
/ingest/directory / /ingest/file / /ingest/url
        ↓
LlamaIndex loader + SentenceSplitter
        ↓
OpenAI embeddings
        ↓
Local in-memory vector index
        ↓
/chat retrieves chunks
        ↓
Strict RAG prompt
        ↓
OpenAI answer generation
        ↓
Answer validation
        ↓
Answer + source chunks
```

## Supabase architecture

```text
Documents
  ↓
Chunk text
  ↓
OpenAI embeddings
  ↓
Supabase Postgres documents table
  ↓
pgvector similarity search
  ↓
Retrieved chunks
  ↓
Strict RAG prompt
  ↓
OpenAI answer
  ↓
Answer validation
  ↓
Answer + citations
```

## Current endpoints

```text
GET  /health
POST /ingest/directory
POST /ingest/file
POST /ingest/url
POST /chat
POST /chat/stream
GET  /usage
```

## Current quality controls

```text
Retrieval score threshold
Source chunks returned with answers
Strict prompt grounding
Post-generation answer validation
Eval set with answerable, unanswerable, ambiguous, and adversarial questions
Usage and latency logging
```

## Business-owner explanation

This system lets a business connect internal knowledge documents, such as policies, FAQs, product information, support guides, PDFs, and website pages.

When a customer or employee asks a question, the system does not simply guess from the AI model’s memory. It first searches the business documents, finds the most relevant sections, and asks the AI to answer using only those sections.

The answer includes source chunks so the business can see which document supported the response.

If the documents do not contain enough information, the system is designed to say that it cannot answer confidently instead of inventing a policy.

This is useful for support teams, internal knowledge bases, onboarding, and businesses with repeated questions spread across messy documentation.