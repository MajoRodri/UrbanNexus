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

class ChangePasswordRequest(BaseModel):
    id_empleado: str
    password_actual: str = Field(..., min_length=6)
    password_nueva: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    id_empleado: str
    nombres: str
    apellidos: str
    email: EmailStr
    rol: str
    activo: bool

    class Config:
        from_attributes = True