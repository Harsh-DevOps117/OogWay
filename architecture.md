# System Architecture - The Lenny Growth Assistant

## 1. Tech Stack
- **API Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase) + `pgvector` extension
- **ORM**: SQLAlchemy
- **Agent/LLM Layer**: LangChain
- **Authentication**: JWT & bcrypt

## 2. Database Schema
### `User`
- Standard auth table containing `email`, `password` (hashed).

### `ChatSession`
- Groups messages together. Contains `id`, `user_id`, `created_at`.

### `Message`
- Individual chat bubbles. Contains `session_id`, `role` (user/assistant), `content`, `artifacts`, and `sources` (JSON).

### `TranscriptChunk`
- The RAG knowledge base. Contains `episode_id`, `content`, and `embedding` (VECTOR 1536).

## 3. Agentic Architecture & Routing
The system uses a smart routing mechanism in `app/services/agent.py`.
1. **Retrieval**: User queries are embedded and compared against `TranscriptChunk` using `cosine_distance`. Top 5 chunks are retrieved.
2. **Intent Detection**: The system scans the query for keywords like "Ship 30 for 30" or "essay".
3. **Routing**:
   - If a standard query: Uses `BASE_SYSTEM_PROMPT` to provide a standard, cited answer.
   - If an essay request: Uses `SHIP30_SYSTEM_PROMPT` to enforce specific word counts, hooks, and formatting.
4. **Artifact Extraction**: If the LLM produces tags like `<artifact>...</artifact>`, the backend strips them from the main content and places them in the `artifacts` database column and API response field.

## 4. Model Toggle (Cloud vs Local)
`app/core/llm_factory.py` acts as a factory pattern. 
By changing `LLM_PROVIDER` in `.env`:
- `LLM_PROVIDER=openai`: Uses GPT-4o-mini and OpenAI embeddings.
- `LLM_PROVIDER=ollama`: Uses local Llama3 and local Nomic embeddings. 
Zero application code needs to be changed.

## 5. Deployment Topology
- **Local Dev**: Run via `uvicorn app.main:app --reload`.
- **Database**: Hosted remotely on Supabase, allowing easy sharing of the populated vector index without needing a massive local Postgres container.
