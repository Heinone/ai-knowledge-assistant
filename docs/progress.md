# Progress Log

## Day 1

Date: 10.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: FastAPI project skeleton, app folder structure, /health endpoint, route module separation, ChatRequest and ChatResponse Pydantic models, stub /chat endpoint
Bug encountered: None recorded
One thing learned: FastAPI routes should stay thin; request/response models act like typed DTOs with validation
Next action: Day 2 — OpenAI provider + real LLM response

---

## Day 2

Date: 10.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: app/config.py with dotenv config loading, OpenAI provider in app/llm/openai_provider.py, /chat wired to real OpenAI response, status/usage/output logging added
Bug encountered: The provider initially returned response.output_text or "", which hid empty/incomplete model responses as normal empty strings
One thing learned: max_output_tokens includes reasoning tokens, not just visible answer text; low limits can cause status=incomplete, truncated output, or empty visible output while still consuming tokens
Next action: Day 3 — LlamaIndex local text ingestion

---

## Day 3

Date: 10.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: build_index.py, data/raw/nordictrail/refund_policy.txt, data/raw/nordictrail/shipping_policy.txt, local LlamaIndex VectorStoreIndex using OpenAI embeddings, multi-question retrieval inspection loop
Bug encountered: LlamaIndex could not see OPENAI_API_KEY until dotenv was loaded and the api_key was passed explicitly; build_index.py also needed to run from repo root with data/ at repo root
One thing learned: Vector retrieval always returns nearest chunks, even when none actually answer the question; unsupported questions need citations, source checking, and refusal behavior
Next action: Day 4 — In-memory RAG service

## Day 4

Date: 10.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: ingestion_service.py, ingest.py route, chat_service.py, /ingest/directory endpoint, /chat wired to in-memory RAG index
Bug encountered: None
One thing learned: In-memory state works for a local prototype, but the index disappears when the server restarts and is shared globally across requests
Next action: Day 5 — Citations + Week 1 review

## Day 5

Date: 10.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: SourceChunk response model, ChatResponse sources list, chat_service returning answer + sources, basic retrieval score refusal threshold
Bug encountered:
One thing learned: Citations are only useful if the source chunk actually supports the answer; returning sources exposes when the model over-answers
Next action: Day 6 — File ingestion + PDF support

## Day 6

Date: 10.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: warranty_policy.txt, inspect_documents.py, build_index_from_file function, /ingest/file endpoint
Bug encountered:
One thing learned: PDF ingestion only works well when the PDF contains extractable text; file ingestion by path is simpler than real upload handling and good enough for this step
Next action: Day 7 — Chunking experiments

## Day 7

Date: 10.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: chunk_inspect.py, explicit SentenceSplitter chunking in ingestion_service.py, chunk_size/chunk_overlap request fields for /ingest/directory and /ingest/file
Bug encountered:
One thing learned: Chunk size changes what context retrieval can see; small chunks reduce noise but may lose context, while large chunks preserve context but may retrieve irrelevant text.
Next action: Day 8 — URL ingestion

## Day 8

Date: 18.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: url_loader.py, /ingest/url endpoint, URL text saved into data/raw/url_imports, URL ingestion wired to existing file ingestion
Bug encountered: Vague question "What is this page about?" failed because no source passed the score threshold, but a more specific question about Example Domain retrieved correctly. The suggested httpbin.org/html test URL was unreliable, so example.com was used as the stable test.
One thing learned: URL ingestion is just document ingestion after fetching and cleaning HTML; retrieval quality depends on page text quality, question specificity, and the retrieval score threshold.
Next action: Day 9 — Claude API comparison

## Day 9

Date: 18.6.20226touch
Blocks completed: 1, 2, 3, 4, 5
Code produced: LLMProvider base class, OpenAIProvider class, ClaudeProvider class or stub, compare_providers.py
Bug encountered:
One thing learned: Provider abstraction lets the app compare OpenAI and Claude behavior without rewriting business logic; unsupported questions expose differences in refusal and context-following.
Next action: Day 10 — Better prompt grounding

## Day 10

Date: 18.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: prompt_builder.py, source IDs in response model, chat_service updated to retrieve chunks then generate answer with a strict RAG prompt
Bug encountered:
One thing learned: Grounding requires both retrieval filtering and prompt rules; the model must be told not to infer unsupported business facts from nearby context.
Next action: Day 11 — Supabase project + pgvector

## Day 11

Date: 24.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: Supabase project, pgvector enabled, documents table, test_supabase.py connection/insert script, SUPABASE_URL and SUPABASE_SERVICE_KEY env vars
Bug encountered:
One thing learned: Supabase pgvector is just Postgres with a vector column; today only inserted plain content/metadata, while embeddings and similarity search come next.
Next action: Day 12 — Store embeddings in Supabase

## Day 12

Date: 24.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: test_embedding.py, insert_embedding.py, match_documents SQL function, search_supabase.py, seed_supabase_chunks.py
Bug encountered:
One thing learned: Supabase pgvector stores embeddings as vector columns, and similarity search works by embedding the question and ordering stored chunks by vector distance.
Next action: Day 13 — Supabase vector store service

## Day 13

Date: 24.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: SupabaseVectorStore, test_supabase_store.py, VECTOR_STORE config switch, ingestion_service Supabase mode, chat_service Supabase retrieval mode
Bug encountered:
One thing learned: Local vector storage and Supabase pgvector use the same RAG idea, but Supabase persists chunks and requires explicit insert/search services instead of relying on in-memory LlamaIndex state.
Next action: Day 14 — Streaming chat

## Day 14

Date: 24.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: /chat/stream endpoint, OpenAIProvider.stream(), stream_answer_question() RAG streaming service
Bug encountered:
One thing learned: Streaming improves perceived latency, but plain text streaming loses structured response fields like sources unless we use a richer protocol.
Next action: Day 15 — Simple frontend widget

## Day 15

Date: 24.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: frontend/widget.html, CORS middleware in app/main.py, browser chat UI calling /chat, optional streaming UI calling /chat/stream
Bug encountered:
One thing learned: A simple frontend makes latency and citation quality more obvious; streaming improves perceived speed but plain text streaming does not return structured sources.
Next action: Day 16 — Evaluation set

## Day 16

Date: 24.6.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: data/evals/nordictrail_eval.json, tests/eval_runner.py, run_eval.sh, latest_eval_results.json
Bug encountered:
One thing learned: Evals expose whether a RAG failure is retrieval, generation, refusal, source citation, or test-expectation related.
Next action: Day 17 — Cost and latency logging

## Day 17

Date: 22.7.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: usage_service.py, OpenAIProvider.generate_with_usage(), retrieval/LLM/total timing in chat_service.py, /usage endpoint
Bug encountered:
One thing learned: Cost and latency visibility requires logging at the provider and service layers; retrieval time, LLM time, token usage, source count, and refusal status tell different parts of the story.
Next action: Day 18 — Guardrails and refusal behavior

## Day 18

Date: 23.7.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: docs/refusal-cases.md, answer_validation_service.py, stricter prompt_builder.py, post-generation validation in chat_service.py
Bug encountered: Evals caught several guardrail issues: warranty answers omitted the manufacturing-defect condition, prompt-injection refund question initially redirected instead of refusing, and ambiguous return questions used the refusal phrase instead of asking clarification. Fixed prompt rules and validator logic until evals passed 7/7.
One thing learned: Guardrails need layers: retrieval threshold, prompt rules, answer validation, and evals. Prompting alone is not enough, and eval failures can reveal subtle overpromising.
Next action: Day 19 — Architecture and consulting explanation

## Day 19

Date: 24.7.2026
Blocks completed: 1, 2, 3, 4, 5
Code produced: docs/architecture.md, docs/risks.md, docs/mvp-offer.md
Bug encountered:
One thing learned: A consulting-ready AI project needs a clear explanation of architecture, risks, limits, and MVP scope — not just working code.
Next action: Day 20 — Final demo + readiness check