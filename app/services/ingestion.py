import os
import glob
from sqlalchemy.orm import Session
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.db.connection_db import SessionLocal
from app.models.chat_model import TranscriptChunk
from app.core.llm_factory import get_embeddings

def ingest_transcripts(episodes_dir: str = "episodes"):
    print(f"Starting ingestion from {episodes_dir}...")
    db = SessionLocal()

    embeddings = get_embeddings()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    episode_folders = glob.glob(os.path.join(episodes_dir, "*"))

    count = 0
    for folder in episode_folders:
        if not os.path.isdir(folder):
            continue

        episode_id = os.path.basename(folder)
        transcript_path = os.path.join(folder, "transcript.md")

        if os.path.exists(transcript_path):
            with open(transcript_path, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"Processing episode: {episode_id}")
            chunks = text_splitter.create_documents([content])

            chunk_texts = [chunk.page_content for chunk in chunks]

            print(f"  Embedding {len(chunk_texts)} chunks...")
            vectors = embeddings.embed_documents(chunk_texts)

            for idx, chunk_text in enumerate(chunk_texts):
                db_chunk = TranscriptChunk(
                    episode_id=episode_id,
                    content=chunk_text,
                    embedding=vectors[idx]
                )
                db.add(db_chunk)

            db.commit()
            count += 1

    print("Ingestion complete!")
    db.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv('app/.env')
    ingest_transcripts()
