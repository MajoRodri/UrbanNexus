from pydantic import BaseModel, EmailStr


class InvitationCreateRequest(BaseModel):
    email: EmailStr
    rol: str


class InvitationResponse(BaseModel):
    id: int
    codigo: str
    email: EmailStr
    rol: str
    usado: bool

    class Config:
        from_attributes = True