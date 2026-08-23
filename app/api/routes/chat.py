from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.connection_db import db_connection
from app.models.user_model import User
from app.models.chat_model import ChatSession, Message
from app.core.security import get_current_user
from app.services.agent import generate_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class SessionResponse(BaseModel):
    id: int
    title: Optional[str]
    created_at: str

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    artifacts: Optional[str] = None
    sources: Optional[List[str]] = None

    class Config:
        from_attributes = True

@router.post("/sessions", response_model=dict)
def create_session(db: Session = Depends(db_connection), current_user: User = Depends(get_current_user)):
    session = ChatSession(user_id=current_user.id, title="New Chat")
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"success": True, "session": {"id": session.id, "title": session.title}}

@router.get("/sessions", response_model=dict)
def get_sessions(db: Session = Depends(db_connection), current_user: User = Depends(get_current_user)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()
    return {"success": True, "sessions": [{"id": s.id, "title": s.title, "created_at": str(s.created_at)} for s in sessions]}

@router.get("/sessions/{session_id}/messages", response_model=dict)
def get_session_messages(session_id: int, db: Session = Depends(db_connection), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    return {
        "success": True, 
        "messages": [
            {
                "id": m.id, 
                "role": m.role, 
                "content": m.content, 
                "artifacts": m.artifacts,
                "sources": m.sources 
            } for m in messages
        ]
    }

@router.post("/sessions/{session_id}/message", response_model=dict)
def send_message(session_id: int, request: ChatRequest, db: Session = Depends(db_connection), current_user: User = Depends(get_current_user)):

    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        response_data = generate_response(session_id, request.message, db)
        return {"success": True, "data": response_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
