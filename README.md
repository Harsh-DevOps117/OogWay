# OogWay (Lenny Growth Assistant)

OogWay is an AI-powered Retrieval-Augmented Generation (RAG) backend designed to act as an intelligent growth assistant. It uses transcripts from Lenny's Podcast to answer user questions, providing accurate, grounded insights with explicit source citations.

## 🚀 Features
- **Retrieval-Augmented Generation (RAG)**: Leverages OpenAI's `text-embedding-3-small` (1536-dimensional vectors) to retrieve contextually relevant podcast chunks.
- **High-Performance Inference**: Uses OpenAI's `gpt-4o-mini` to synthesize answers based strictly on the retrieved context, preventing hallucinations.
- **Secure Authentication**: Fully implemented JWT (JSON Web Token) authentication flow with strict password constraints (capped at 72 bytes) hashed via `bcrypt`.
- **Robust Database**: Hosted on Supabase (PostgreSQL) using the `pgvector` extension for lightning-fast cosine similarity vector searches.
- **Dockerized**: Fully containerized for easy deployment, optimized with PyTorch CPU indexing to keep image sizes incredibly lean.

## 🛠️ Tech Stack
- **Backend Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL (Supabase) + `pgvector`
- **ORM**: SQLAlchemy
- **AI/LLM orchestration**: LangChain (`langchain-openai`)
- **Containerization**: Docker & Docker Compose

## ⚙️ Environment Variables
Create an `app/.env` file with the following variables:
```env
# Database
db_uri=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres

# Supabase Auth specifics
host=db.[PROJECT_ID].supabase.co
port=5432
database=postgres
user=postgres

# Security
SECRET_KEY="your-secure-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Providers
LLM_PROVIDER="openai"
OPENAI_API_KEY="sk-..."
GROQ_API_KEY="gsk_..." # Optional, if switching to Groq
```

## 📦 Running Locally (Virtual Environment)
1. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🐳 Running with Docker
The app is fully containerized. You do not need to install Python locally.
```bash
# Build and start the container in the background
docker-compose up -d --build

# View logs
docker-compose logs -f web
```
The API will be available at `http://localhost:8000`.

## 🧠 Data Ingestion
To populate the database with podcast transcripts:
1. Ensure your markdown files are placed inside the `episodes/` directory (e.g., `episodes/brian-chesky/transcript.md`).
2. Run the ingestion script:
   ```bash
   python -m app.services.ingestion
   ```
*Note: The chunking strategy uses a size of 1000 characters and a 200 character overlap to preserve conversational context.*

## 📚 API Endpoints
- **Health Check**: `GET /health`
- **Auth**: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`
- **Chat**: `POST /api/v1/chat/sessions`, `POST /api/v1/chat/sessions/{session_id}/message`
