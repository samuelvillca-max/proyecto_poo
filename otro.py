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
class metodo_de_pago:
    def __init__(self, monto):
        self.monto= monto
    def procesar_pago(self):
        print("verificando...")
class QR(metodo_de_pago):
    def __init__(self, monto, codigo):
        super().__init__(monto)
        self.codigo = codigo
    def procesar_pago(self):
        print("Procesando pago con QR...")
        print(f"Monto: {self.monto}, Código: {self.codigo}")
class Efectivo(metodo_de_pago):
    def __init__(self, monto, recibo):
        super().__init__(monto)
        self.recibo= recibo
        
    def procesar_pago(self):
        super().procesar_pago()
        print(f"el monto es: {self.monto}, Recibo: {self.recibo}")
class Tarjeta(metodo_de_pago):
    def __init__(self, monto, numero_tarjeta):
        super().__init__(monto)
        self.numero_tarjeta = numero_tarjeta
    def procesar_pago(self):
        print("Procesando pago con tarjeta...")
        print(f"Monto: {self.monto}, Número de tarjeta: {self.numero_tarjeta}")