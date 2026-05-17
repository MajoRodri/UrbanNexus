import random


LETRAS_ROL = {
    "admin": "P",
    "tecnico": "T",
    "visualizador": "V"
}

#Genera un identificador interno de empleado, con el formato Role-N
def generate_employee_id(rol: str) -> str:

    if rol not in LETRAS_ROL:
        raise ValueError("Rol no válido para generar ID")

    letra_rol = LETRAS_ROL[rol]
    numero = random.randint(1000, 9999)

    return f"E{numero}{letra_rol}"

def generate_unique_id(rol: str, db, Usuario) -> str:
    # Genera IDs hasta encontrar uno que no exista en la BD.
    # El espacio es de 9000 números posibles (1000-9999), así que en la práctica
    # el bucle termina en el primer intento salvo que haya cientos de usuarios del mismo rol.
    while True:
        id_empleado = generate_employee_id(rol)

        existing_user = db.query(Usuario).filter(Usuario.id_empleado == id_empleado).first()

        if not existing_user:
            return id_empleado
