from metodo_de_pago import metodo_de_pago
class Tarjeta(metodo_de_pago):
    def __init__(self, monto, numero_tarjeta):
        super().__init__(monto)
        self.numero_tarjeta = numero_tarjeta
    def procesar_pago(self):
        print("Procesando pago con tarjeta...")
        print(f"Monto: {self.monto}, Número de tarjeta: {self.numero_tarjeta}")