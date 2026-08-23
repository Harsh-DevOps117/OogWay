import numbers
from pydantic import BaseModel,Field


class user_registration(BaseModel):
    name:str = Field(...,min_length=3,max_length=100,description="Name must be a string of at least 3 characters",example="Harish Kumar")
    email:str = Field(...,pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    mobile:str = Field(...,min_length=10,max_length=15,description="Mobile number")
    password:str = Field(...,min_length=8,max_length=32,description="Password must be a string of at least 8 characters",example="[PASSWORD]")
class login(BaseModel):
    email:str = Field(...,pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password:str = Field(...,min_length=8,max_length=32)

class user_login_response(BaseModel):
    id :int
    name:str
    email:str
    access_token:str
    token_type:str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    mobile: str

    class Config:
        from_attributes = True
