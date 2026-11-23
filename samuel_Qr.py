from metodo_de_pago import metodo_de_pago
class QR(metodo_de_pago):
    def __init__(self, monto, codigo):
        super().__init__(monto)
        self.codigo = codigo
    def procesar_pago(self):
        print("Procesando pago con QR...")
        print(f"Monto: {self.monto}, Código: {self.codigo}")