from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.db.connection_db import db_connection
from app.schemas.user_schema import user_registration, UserResponse, user_login_response
from app.services.user_registration import register_user
from app.services.user_login import login_user
from app.core.security import get_current_user
from app.models.user_model import User

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_data: user_registration, db: Session = Depends(db_connection)):
    return register_user(user_data, db)

@router.post("/login", response_model=user_login_response)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_connection)):
    return login_user(form_data, db)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
