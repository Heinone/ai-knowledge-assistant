# AI Knowledge Assistant

A reusable Business Knowledge Base Agent built with RAG (Retrieval Augmented Generation).

The system allows businesses to upload their own documents and provide a grounded AI assistant that answers questions using company-specific knowledge.

The same architecture can support:

- Customer support assistants
- Internal employee knowledge assistants
- Product documentation assistants
- Business process assistants

---

# Demo Use Cases

## Aster & Loom — Customer Support Assistant

A premium clothing brand example.

The assistant can answer questions about:

- Product details
- Materials and sourcing
- Manufacturing locations
- Care instructions
- Returns and shipping policies
- Latest product drops

Example:

> "Where is the Vale Linen Overshirt made?"

The assistant retrieves the relevant product and manufacturing information and provides a grounded answer.

---

## Vertex Systems — Internal Knowledge Assistant

A software company example.

The assistant can help employees find information from:

- Technical documentation
- Internal processes
- Engineering guidelines
- Company policies

The same AI system is reused with a different knowledge base.

---

# Architecture

```
User
 |
 v
Chat Interface
 |
 v
FastAPI Backend
 |
 +----------------+
 |                |
 v                v
Retriever        LLM
 |
 v
Vector Store
 |
 v
Grounded Answer
```

---

# Core Features

## Document ingestion

Supports:

- Markdown
- TXT
- PDF

Uploaded documents are:

1. Loaded
2. Split into chunks
3. Converted into embeddings
4. Stored for semantic search

---

## Retrieval Augmented Generation (RAG)

The assistant does not answer from general knowledge.

Flow:

1. User asks a question
2. Relevant document chunks are retrieved
3. Retrieved context is added to the prompt
4. The LLM generates a grounded answer

---

## Grounding and Safety

The system includes:

- Refusal behaviour when information is unavailable
- Prompt injection protection
- Answer validation
- Source tracking
- Evaluation tests

---

# Technology Stack

## Backend

- Python
- FastAPI
- OpenAI API
- LlamaIndex
- Supabase pgvector

## Frontend

- HTML
- CSS
- JavaScript

## AI

- OpenAI embeddings
- GPT models
- Optional multi-provider support

---

# Project Structure

```
app/
├── routes/
├── services/
├── llm/
├── vector_store/
└── models/

frontend/
├── chat.html
├── admin.html
├── styles.css
└── api.js

data/
├── raw/
│   ├── customer_demo/
│   ├── internal_demo/
│   └── test_fixtures/
└── evals/

tests/
```

---

# Running Locally

## 1. Create environment

```bash
python -m venv venv
source venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Add environment variables

Create:

```
.env
```

Example:

```env
OPENAI_API_KEY=your_key_here
DEFAULT_MODEL=gpt-5-mini
```

## 4. Start backend

```bash
uvicorn app.main:app --reload
```

## 5. Open frontend

Serve the frontend:

```bash
cd frontend
python3 -m http.server 5500
```

Open:

```
http://localhost:5500/admin.html
```
Upload the knowledge documents (Current support for txt,md and pdf files). Then navigate to:
```
http://localhost:5500/chat.html
```

---

# Evaluation

The project includes RAG evaluation cases covering:

- Answerable questions
- Unanswerable questions
- Ambiguous questions
- Prompt injection attempts

Run:

```bash
./run_eval.sh
```

---

# Future Improvements

Planned:

- Multi-tenant business configuration
- Authentication
- Conversation memory
- Production deployment
- Analytics dashboard
- Cost monitoring
- Human escalation workflows

---

# Goal

Build AI assistants that help businesses turn their existing knowledge into useful, reliable conversations.