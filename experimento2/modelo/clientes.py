
class Cliente:
    def __init__(self, nombre, telefono):
        self.nombre = nombre
        self.telefono = telefono
        self._pedidos = []

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        valor = str(valor).strip()
        if not Cliente.validar_telefono(valor):
            raise ValueError("El teléfono debe tener 8 dígitos y comenzar con 6 o 7.")
        self._telefono = valor

    @property
    def pedidos(self):
        return list(self._pedidos)

    @staticmethod
    def validar_telefono(telefono):
        telefono = str(telefono).strip()
        return len(telefono) == 8 and telefono.isdigit() and telefono[0] in ("6", "7")

    def realizar_pedido(self, pedido):
        self._pedidos.append(pedido)

    def __str__(self):
        return f"{self.nombre} - Tel. {self.telefono}"