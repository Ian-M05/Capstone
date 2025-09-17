from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    username: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
