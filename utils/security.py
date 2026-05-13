from passlib.context import CryptContext

# bcrypt: algoritmo de hashing lento por diseño; añade sal aleatoria automáticamente
# y es resistente a ataques de fuerza bruta gracias a su coste computacional configurable.
# "deprecated=auto" actualiza automáticamente hashes viejos al hacer verify.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    # Genera un hash bcrypt con sal única por cada llamada; nunca guardar la contraseña en plano.
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    # Compara la contraseña enviada contra el hash almacenado sin necesidad de conocer la sal.
    return pwd_context.verify(password, password_hash)