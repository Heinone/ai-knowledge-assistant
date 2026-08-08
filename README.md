# Answer.ly

Answer.ly is a configurable Business Knowledge Base Agent built with RAG (Retrieval Augmented Generation).

Businesses can upload their own documents, configure one or more AI assistants, and provide grounded answers based on company knowledge.

The current project is designed as a consulting-grade demo showing how the same RAG platform can support both customer-facing and internal business assistants.

---

## Core Features

### RAG-powered chat

The request flow is:

1. User asks a question
2. Relevant document chunks are retrieved
3. Retrieved context is added to the prompt
4. The LLM generates a grounded answer
5. Supporting document sources are returned when appropriate

If the knowledge base does not contain enough information, the assistant returns a configured fallback instead of inventing an answer.

---

### Multiple assistant modes

Answer.ly currently supports:

- `customer_support`
- `internal_knowledge`

A deployment can provision either one mode or both.

When only one mode is enabled, it is resolved automatically.

When multiple modes are enabled, the request must explicitly specify the assistant mode.

---

### Document management

Supported document formats:

- PDF
- TXT
- Markdown

The admin interface supports:

- Uploading documents
- Indexing documents
- Viewing indexed documents
- Deleting documents
- Rebuilding the assistant knowledge base

Documents and indexes are isolated by assistant mode.

---

### Assistant configuration

Each assistant can configure:

- Assistant name
- Chat name
- Tone
- Response length
- Default language
- Supported languages
- Greeting
- Fallback message
- Contact information

Internal knowledge assistants can also enable document citations.

---

### Branding

Company branding currently supports:

- Logo
- Favicon
- Assistant avatar

If no assistant avatar is configured, Answer.ly uses a default assistant avatar.

Company chat-colour customization is retained in the configuration model but is not currently applied to the demo UI.

---

### Grounding and safety

The system includes:

- Retrieval score thresholds
- Grounded-answer prompting
- Configurable refusal behaviour
- Answer validation
- Prompt-injection resistance
- Source tracking
- Assistant-mode knowledge isolation

Fallback answers do not expose retrieved document sources.

---

## Architecture

```text
Browser
   |
   v
HTML / CSS / JavaScript
   |
   v
FastAPI
   |
   +---------------------+
   |                     |
   v                     v
Retriever              LLM provider
   |                     |
   v                     v
Vector index        Grounded answer
   |
   v
Uploaded documents
```

The backend separates:

- API routes
- Application services
- Configuration
- Assistant modes
- LLM providers
- Vector storage

The LLM layer uses a provider abstraction so additional model providers can be added without rewriting the RAG pipeline.

---

## Technology Stack

### Backend

- Python
- FastAPI
- LlamaIndex
- OpenAI API
- SQLite document registry

### AI

- OpenAI embeddings
- GPT models
- Provider abstraction for additional LLM APIs

### Vector storage

Current demo:

- Local persisted vector indexes

Also present:

- Supabase / pgvector integration

The local vector store is the primary path for the current demo.

### Frontend

- HTML
- CSS
- Vanilla JavaScript

---

## Project Structure

```text
app/
├── config/
├── llm/
├── models/
├── prompts/
├── routes/
├── services/
├── vector_store/
└── main.py

data/
├── answerly/
├── company/
├── documents/
├── examples/
├── indexes/
└── uploads/

frontend/
├── assets/
├── admin.html
├── admin.js
├── admin-assistants.js
├── admin-onboarding.js
├── api.js
├── chat.html
├── config.js
└── styles.css

scripts/
├── activate_example_company.py
├── reset_app_state.py
└── ...

tests/

start-demo.sh
pytest.ini
```

Runtime company data, uploaded documents, indexes, and generated runtime configuration are intentionally kept separate from tracked demo fixtures.

---

## Local Setup

### 1. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a root `.env` file.

Example:

```env
OPENAI_API_KEY=your_key_here
DEFAULT_MODEL=gpt-5-mini
VECTOR_STORE=local
AVAILABLE_MODES=customer_support,internal_knowledge
```

`.env.runtime` is generated automatically by the demo tooling and overrides deployment-specific runtime settings.

Do not commit API keys.

---

## Start the Demo

From the project root:

```bash
./start-demo.sh
```

The launcher provides four options:

```text
1) Reset to Answer.ly
2) Start Aster & Loom
3) Start Vertex Systems
4) Start Northstar eBikes
```

When resetting to Answer.ly, you can choose:

```text
1) Internal knowledge
2) Customer support
3) Both
```

The launcher:

- Resets or activates the selected demo configuration
- Starts the FastAPI backend
- Starts the frontend HTTP server
- Stops both servers with `Ctrl+C`

Open:

```text
Admin
http://localhost:5500/admin.html

Chat
http://localhost:5500/chat.html
```

For Northstar's dual-mode demo:

```text
Customer support
http://localhost:5500/chat.html?mode=customer_support

Internal knowledge
http://localhost:5500/chat.html?mode=internal_knowledge
```

---

## Demo Companies

### Aster & Loom

Customer support assistant for a premium clothing brand.

The assistant answers questions about:

- Products and materials
- Manufacturing
- Care instructions
- Shipping and returns
- Store information
- Product collections

This demo uses the `customer_support` assistant mode.

---

### Vertex Systems

Internal knowledge assistant for a software company.

The assistant answers employee questions about:

- Production access
- Engineering procedures
- Incident escalation
- Production change policies
- Internal operational processes

This demo uses the `internal_knowledge` assistant mode and can display document citations.

---

### Northstar eBikes

Dual-assistant demo showing strict knowledge-base separation.

It includes:

- Customer support assistant
- Internal knowledge assistant

The customer assistant can answer warranty questions but cannot access internal approval procedures.

The internal assistant can answer operational questions such as battery replacement approval rules.

This demo demonstrates assistant-mode isolation within the same company deployment.

---

## Manual Demo Activation

The demo companies can also be activated directly.

```bash
venv/bin/python -m scripts.activate_example_company aster_loom --apply

venv/bin/python -m scripts.activate_example_company vertex_systems --apply

venv/bin/python -m scripts.activate_example_company northstar_ebikes --apply
```

Reset all runtime state:

```bash
venv/bin/python -m scripts.reset_app_state
```

---

## Tests

Run the unit test suite:

```bash
venv/bin/python -m pytest
```

The test suite covers areas including:

- Assistant mode resolution
- Deployment mode provisioning
- Assistant settings
- Fallback settings
- Configuration migration
- Document registry behaviour
- Mode-isolated ingestion
- Prompt construction

---

## Current Scope

The current goal is a reliable client-demo and consulting prototype.

Production features such as these would be added based on client requirements:

- Authentication and authorization
- SSO
- Rate limiting
- Production multi-tenancy
- Cloud storage
- Enterprise observability
- Advanced analytics
- Billing
- Production deployment hardening

---

## Goal

Answer.ly demonstrates how a business can turn its existing documents into grounded AI assistants while keeping different assistant use cases and knowledge bases isolated.

The project is also designed to serve as a reusable foundation for client-specific AI knowledge systems.