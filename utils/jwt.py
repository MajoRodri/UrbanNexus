from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status

# Mover a variable de entorno antes de pasar a producción para no exponer la clave en el código
SECRET_KEY = "CAMBIA_ESTA_CLAVE_SUPER_SECRETA"
# HS256: firma simétrica; ambas partes (Flask y FastAPI) usan la misma SECRET_KEY
ALGORITHM = "HS256"
# El token expira en 1 hora; ajustar según política de seguridad del proyecto
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    # Añade la fecha de expiración al payload y firma el JWT con la clave secreta.
    # El campo "sub" dentro de data debe ser el id_empleado del usuario.
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


def verify_access_token(token: str):
    # Decodifica y valida el JWT; lanza 401 automáticamente si el token está
    # mal formado, la firma no coincide o la fecha de expiración ya pasó.
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado."
        )