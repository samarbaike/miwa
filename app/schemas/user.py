from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    
    username: str = Field(min_length=5, max_length=50)
    email: EmailStr 
    password: str = Field(min_length=8)

class LoginRequest(BaseModel):

    username: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=8)
    
class UserResponse(BaseModel):

    id: int = Field(gt=0)
    username: str = Field(min_length=5, max_length=50)
    email: EmailStr
    elo: int = Field()

class UserStats(BaseModel):

    elo: int
    wins: int = Field(ge=0)
    streak: int = Field(ge=0)
    total_matches: int = Field(ge=0)

class UserUpdate(BaseModel):

    username: Optional[str] = Field(min_length=5, max_length=50)