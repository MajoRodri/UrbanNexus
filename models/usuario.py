class Usuario:
    def __init__(self, num_empleado, nombre, apellidos, password_hash):
        self.num_empleado = num_empleado
        self.nombre = nombre
        self.apellidos = apellidos
        self.password_hash = password_hash

    def to_dict(self):
        return {
            "num_empleado": self.num_empleado,
            "nombre": self.nombre,
            "apellidos": self.apellidos,
            "password_hash": self.password_hash
        }
