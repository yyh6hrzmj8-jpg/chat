from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class UserOut(BaseModel):
    id: int
    email: EmailStr

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
