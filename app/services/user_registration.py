from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user_model import User, Base
from app.db.connection_db import engine
from app.schemas.user_schema import user_registration, UserResponse
from app.core.security import get_password_hash


Base.metadata.create_all(bind=engine)

def register_user(user_data: user_registration, db: Session):

    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )


    hashed_password = get_password_hash(user_data.password)


    new_user = User(
        name=user_data.name,
        email=user_data.email,
        mobile=user_data.mobile,
        password=hashed_password
    )


    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
