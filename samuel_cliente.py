class Cliente:
    def __init__(self, nombre, telefono):
        self.nombre = nombre
        self.telefono = str(telefono)
    def pedidos(self):
        print("pedido")
    def validar(self):
        if len(self.telefono) <= 8 and len(self.telefono) > 0:
            print("El número de teléfono es valido.")
        else: 
            print("El número de teléfono es inválido.")
            

class Cliente:
    def _init_(self, nombre, telefono):
        self.nombre = nombre
        self.telefono = telefono

    def validar_telefono(self):
        return self.telefono.isdigit() and len(self.telefono) == 8

    def realizar_pedido(self, pedido):
        pedido.cliente = self
        return pedido