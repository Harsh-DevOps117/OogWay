# Key Architectural & Technical Decisions (OogWay)

This document tracks the major technical decisions made during the development of the Lenny Growth Assistant backend.

## 1. Embedding Model: `all-MiniLM-L6-v2` (HuggingFace)
- **Decision:** We migrated away from OpenAI (`text-embedding-3-small`) and Ollama (`nomic-embed-text`) to use the HuggingFace `all-MiniLM-L6-v2` model locally via `sentence-transformers`.
- **Reason:** To enable a serverless-friendly, cost-effective RAG operation. Running embeddings locally in-memory removes the latency and cost of external API calls (OpenAI) and avoids the heavy system overhead of running an Ollama daemon.
- **Impact:** Required updating the database schema.

## 2. Vector Database Dimension: 384
- **Decision:** Updated the PostgreSQL `pgvector` column dimension in the `transcript_chunks` table from `1536` to `384`.
- **Reason:** `1536` is the dimension for OpenAI embeddings. The new `all-MiniLM-L6-v2` model outputs a 384-dimensional vector. This schema update was required to fix the `DataException` dimension mismatch errors.
- **Impact:** All RAG chunks are now efficiently stored in 384 dimensions on Supabase.

## 3. LLM Provider: Groq (`qwen/qwen3.6-27b`)
- **Decision:** Integrated Groq API for the primary text generation via `langchain_groq`.
- **Reason:** Groq provides ultra-low latency inference, which is critical for a smooth conversational UI experience in the frontend. It is much faster and often cheaper than OpenAI for this specific use case.

## 4. Vector Storage: Supabase (PostgreSQL + pgvector)
- **Decision:** Used a hosted Supabase PostgreSQL instance with the `pgvector` extension rather than a local dockerized database.
- **Reason:** Centralized state. The transcripts are already chunked and embedded in this remote database, meaning local development doesn't require a heavy local database container or re-running the heavy ingestion script every time the environment is reset.

## 5. Dockerization & PyTorch CPU Optimization
- **Decision:** Containerized the FastAPI application using Docker. Specifically added `--extra-index-url https://download.pytorch.org/whl/cpu` to the `pip install` step in the `Dockerfile`.
- **Reason:** The HuggingFace embedding model depends on `sentence-transformers`, which depends on `torch`. By default, pip downloads the CUDA-enabled version of PyTorch (~3GB+). Since the embeddings are small and fast enough to run on the CPU, forcing the CPU-only version of PyTorch reduced the Docker image size drastically and cut the build time from hours/minutes down to seconds.
- **Network Issue Fix:** Added `network_mode: "host"` to `docker-compose.yml` to resolve IPv6 routing issues between the Docker bridge network and Supabase.

## 6. Security: 72-Byte Password Limit
- **Decision:** Enforced a maximum password length validation (72 bytes) during user registration (`app/core/security.py`).
- **Reason:** The `bcrypt` hashing algorithm (via `passlib`) has a known limitation where it truncates or throws overflow errors if the input password exceeds 72 bytes. This prevents backend crashes on malicious or overly long inputs.
