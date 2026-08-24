import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage
from app.models.chat_model import ChatSession, Message, TranscriptChunk
from app.core.llm_factory import get_llm, get_embeddings


BASE_SYSTEM_PROMPT = """You are 'The Lenny Growth Assistant', an AI assistant strictly grounded in Lenny's Podcast transcripts.
Your primary role is to answer questions regarding product management, growth, and careers, using only the context provided.
If the answer is not in the context, you must clearly state that you don't know based on the available material.
When answering, explicitly cite the episode sources provided in the context.

If the user asks to generate a document, HTML, or CSS snippet, wrap that specific generated artifact in <artifact> tags so it can be rendered separately.
"""

SHIP30_SYSTEM_PROMPT = """You are an expert ghostwriter creating a 'Ship 30 for 30' style essay based strictly on Lenny's Podcast transcripts.
Your essay must meet these exact constraints:
1. Approximately 1,250 words.
2. Have a strong hook and clear narrative progression.
3. Use skimmable formatting (headings, bullet points, and selective bold emphasis).
4. Deliver a specific, useful takeaway.
5. All claims must be grounded in the provided transcript context.

Return ONLY the essay text, wrapped in <artifact> tags.
"""

def retrieve_context(query: str, db: Session, limit: int = 5) -> tuple[str, List[str]]:
    """Retrieves top K chunks using cosine distance."""
    embeddings = get_embeddings()
    query_vector = embeddings.embed_query(query)


    results = db.query(TranscriptChunk).order_by(
        TranscriptChunk.embedding.cosine_distance(query_vector)
    ).limit(limit).all()

    context_parts = []
    sources_dict = {}
    for row in results:
        context_parts.append(f"[Source: {row.episode_id}]\n{row.content}")
        
        if row.episode_id not in sources_dict:
            sources_dict[row.episode_id] = {
                "episode_id": row.episode_id,
                "title": row.title,
                "guest": row.guest,
                "youtube_url": row.youtube_url,
                "timestamps": set()
            }
        
        if row.timestamp:
            sources_dict[row.episode_id]["timestamps"].add(row.timestamp)

    final_sources = []
    for src in sources_dict.values():
        src["timestamps"] = sorted(list(src["timestamps"]))
        final_sources.append(src)

    return "\n\n".join(context_parts), final_sources

def generate_response(session_id: int, user_query: str, db: Session) -> Dict:
    """End-to-end agent logic for a given chat query."""


    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise ValueError("Session not found")

    title_updated = False
    if not session.title or session.title == "New Chat":
        try:
            title_prompt = f"Summarize this user query into a concise 3 to 5 word title. Return ONLY the title text, nothing else. Query: {user_query}"
            title_llm = get_llm()
            title_response = title_llm.invoke(title_prompt)
            session.title = title_response.content.strip().strip('"\'')
            db.commit()
            title_updated = True
        except Exception:
            pass

    user_msg = Message(session_id=session_id, role="user", content=user_query)
    db.add(user_msg)
    db.commit()

    context_str, sources = retrieve_context(user_query, db)


    is_ship30 = "ship 30" in user_query.lower() or "essay" in user_query.lower()
    system_instruction = SHIP30_SYSTEM_PROMPT if is_ship30 else BASE_SYSTEM_PROMPT

    full_prompt = f"Context from Lenny's Podcast:\n{context_str}\n\nUser Query:\n{user_query}"


    llm = get_llm()
    
    from langchain_core.messages import AIMessage
    previous_msgs = db.query(Message).filter(
        Message.session_id == session_id,
        Message.id != user_msg.id
    ).order_by(Message.created_at.asc()).all()

    messages = [
        SystemMessage(content=system_instruction)
    ]
    
    for msg in previous_msgs[-6:]:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))

    messages.append(HumanMessage(content=full_prompt))


    response = llm.invoke(messages)
    content = response.content


    artifact_str = None
    if "<artifact>" in content and "</artifact>" in content:
        start_idx = content.find("<artifact>") + len("<artifact>")
        end_idx = content.find("</artifact>")
        artifact_str = content[start_idx:end_idx].strip()



    ai_msg = Message(
        session_id=session_id, 
        role="assistant", 
        content=content,
        artifacts=artifact_str,
        sources=json.dumps(sources)
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return {
        "id": ai_msg.id,
        "role": ai_msg.role,
        "content": ai_msg.content,
        "artifacts": ai_msg.artifacts,
        "sources": sources,
        "session_title": session.title if title_updated else None
    }
