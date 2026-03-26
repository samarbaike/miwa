from pydantic import BaseModel, Field, EmailStr

class UserRegister(BaseModel):
    
    username: str = Field(min_length=5, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)

class UserResponse(BaseModel):

    id: int = Field(gt=0)
    username: str = Field(min_length=5, max_length=50)
    email: EmailStr
    rank: int = Field()

class UserStats(BaseModel):

    rank: int
    wins: int = Field(ge=0)
    streak: int = Field(ge=0)
    total_matches: int = Field(ge=0)