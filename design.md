# System Design & Architecture (OogWay)

This document outlines the complete architectural plan, structural decisions, model selections, and ingestion patterns for the **Lenny Growth Assistant** platform.

## 1. High-Level Architecture
The system operates on a client-server architecture designed for high-performance Retrieval-Augmented Generation (RAG):
* **Backend Framework:** FastAPI (Python) for rapid, asynchronous API endpoints (`/auth`, `/chat`).
* **Database:** Supabase PostgreSQL.
* **Vector Storage:** The PostgreSQL `pgvector` extension is used to store and execute similarity searches against embedded chunks.
* **ORM:** SQLAlchemy for robust relational mapping between Users, Chat Sessions, and Transcript Chunks.
* **Authentication:** JWT (JSON Web Tokens) with `bcrypt` password hashing (capped at 72-bytes to prevent passlib overflow).

## 2. Model Selection
We have standardized on **OpenAI** for both the embedding pipeline and the conversational agent:

### Text Generation (LLM)
* **Model:** `gpt-4o-mini`
* **Provider:** OpenAI (`langchain_openai.ChatOpenAI`)
* **Temperature:** `0` (Strictly deterministic to prevent hallucinations and strictly adhere to the transcript data).

### Embeddings
* **Model:** `text-embedding-3-small`
* **Provider:** OpenAI (`langchain_openai.OpenAIEmbeddings`)
* **Vector Dimension:** `1536` (Configured explicitly in `TranscriptChunk` model via `Vector(1536)`).

## 3. Data Ingestion & Chunking Pattern
To ensure the LLM can accurately retrieve and synthesize information from long podcast episodes, we utilize a specific chunking strategy during ingestion (`app/services/ingestion.py`):

* **Splitter Strategy:** `RecursiveCharacterTextSplitter` from LangChain.
* **Chunk Size:** `1000` characters.
* **Chunk Overlap:** `200` characters.
  * *Reasoning:* A 200-character overlap prevents critical context (like the middle of a sentence or the connection between a question and an answer) from being awkwardly cut in half between two database chunks.
* **Separator Regex:** `False` (Relies on standard recursive splitting by paragraphs, then sentences, then words).

## 4. RAG Pipeline Execution
When a user asks a question, the system follows this workflow:
1. **Query Embedding:** The user's question is embedded using `text-embedding-3-small` into a 1536-dimensional vector.
2. **Vector Search:** The database uses cosine similarity (or L2 distance) via `pgvector` to find the most relevant `TranscriptChunk` rows.
3. **Context Injection:** The retrieved chunks are concatenated and injected into the system prompt for `gpt-4o-mini`.
4. **Response Constraints:** The LLM is strictly prompted to:
   * Only answer based on the provided transcript chunks.
   * Explicitly cite the episode sources using the format `[Source: episode-name]`.
   * Return specialized `<artifact>` tags if a complex structural element (like a framework or list) needs to be rendered natively in the frontend UI.
5. **Session Storage:** Both the user query and the LLM response (along with parsed sources and artifacts) are persisted in the `messages` table under a specific `ChatSession`.
