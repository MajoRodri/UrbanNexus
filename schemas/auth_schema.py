from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    nombres: str = Field(..., min_length=3, description="Nombres del usuario")
    apellidos: str = Field(..., min_length=3, description="Apellidos del usuario")
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")
    codigo_invitacion: str = Field(..., description="Código de invitación")

class LoginRequest(BaseModel):
    id_empleado: str = Field(..., description="ID interno del empleado")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

class UserResponse(BaseModel):
    id: int
    employee_id: str
    nombres: str
    apellidos: str
    email: EmailStr
    rol: str
    activo: bool

    class Config:
        from_attributes = True