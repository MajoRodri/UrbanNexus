from pydantic import BaseModel, EmailStr


class InvitationCreateRequest(BaseModel):
    nombres: str
    apellidos: str
    email: EmailStr
    rol: str


class InvitationResponse(BaseModel):
    id: int
    codigo: str
    nombres: str
    apellidos: str
    email: EmailStr
    rol: str
    usado: bool

    class Config:
        from_attributes = True