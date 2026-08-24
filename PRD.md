# Product Requirements Document (PRD) - The Lenny Growth Assistant

## 1. User & Problem
**User**: Internal product managers, growth engineers, and marketers on the growth team.
**Problem**: The team frequently needs actionable insights from Lenny's Podcast transcripts. Currently, finding specific advice or formatting it into readable content (like Ship 30 for 30 essays) requires manual searching, reading, and synthesizing, which is slow and breaks their workflow.
**Solution**: A conversational AI assistant that retrieves transcript data instantly, answers complex questions, and generates formatted artifacts (Markdown/HTML).

## 2. Success Metrics
- **Retrieval Accuracy**: 95%+ of generated answers successfully cite relevant episodes.
- **Latency**: Cloud-based queries resolve in under 3 seconds; Local (Ollama) queries under 10 seconds.
- **Task Completion**: Users can generate a "Ship 30 for 30" essay without needing to manually prompt engineering the LLM.

## 3. Assumptions
- The database (Supabase) has sufficient capacity and `pgvector` enabled for indexing.
- The UI frontend (to be built by another team) will handle the rendering of `<artifact>` tags.
- Transcripts are largely clean markdown without excessive noise.
- The default local testing environment will use Ollama with a small model (e.g. `llama3` or `phi3`).

## 4. Scope Choices
**Included**:
- Core conversational RAG over transcripts.
- Strict "Ship 30 for 30" skill routing.
- Artifact extraction logic in the backend.
- Full API versioning (v1).
- Model toggling via environment variables.

**Excluded**:
- Frontend implementation (out of scope for this backend API engagement).
- User management UI (auth APIs are provided, but no UI).
- Real-time streaming (SSE/WebSockets). To simplify the initial demo and evaluator experience, responses are synchronous.

## 5. Risks & Trade-offs
- **Hallucinations**: The LLM might use external knowledge. *Mitigation: Strict system prompts demanding answers ONLY from provided context.*
- **Local Model Latency**: Running Ollama locally is slow on older hardware. *Trade-off: Allowed for demo purposes, but Cloud (OpenAI/Anthropic) is recommended for production.*
- **Context Window**: Transcripts are long. We are chunking them to 1000 chars to avoid blowing out context limits and improve search granularity.
- **Artifact Security**: Generated HTML/CSS might include malicious scripts if rendered unsafely. *Mitigation: The frontend MUST sanitize (e.g., DOMPurify) any HTML before injecting it into the DOM.*

## 6. Flows
1. **User Authentication Flow**: User sends credentials -> FastAPI validates/hashes -> Returns JWT -> User attaches JWT to subsequent requests as a Bearer token.
2. **Chat & RAG Flow**: User sends question -> Backend fetches history -> Generates embedding -> Vector Search in Supabase -> Assembles context -> Calls LLM (OpenAI/Groq/Ollama) -> Returns structured response -> Saves to Postgres.
3. **Skill Routing Flow**: User includes keywords ("ship 30", "essay") -> Agent logic intercepts -> Swaps system prompt for Ship 30 constraints -> LLM generates artifact -> Returns response with `<artifact>` wrapper.

## 7. Acceptance Criteria
- [x] Backend connects securely to Supabase PostgreSQL.
- [x] The `LLM_PROVIDER` environment variable toggles smoothly between `openai`, `groq`, and `ollama` without code changes.
- [x] Ingestion script successfully chunks markdown files and embeds them.
- [x] Chat endpoint answers questions grounded ONLY in the retrieved transcript context.
- [x] Responses explicitly cite their source (e.g., `[Source: brian-chesky]`).
- [x] Ship 30 for 30 essay generation is correctly routed, generating ~1,250 words wrapped in `<artifact>` tags.

## 8. Implementation Plan
- **Phase 1**: Database schema setup (SQLAlchemy models) & Auth module.
- **Phase 2**: Local Markdown parsing & embedding ingestion pipeline (`RecursiveCharacterTextSplitter`).
- **Phase 3**: RAG Agent Logic (`retrieval_context` + `generate_response`).
- **Phase 4**: LLM Factory pattern to support multiple providers (OpenAI, Groq, local Ollama).
- **Phase 5**: Dockerization & CPU torch optimization to ensure a clean 1-command handoff.
