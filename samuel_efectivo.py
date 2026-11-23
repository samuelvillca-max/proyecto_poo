from metodo_de_pago import metodo_de_pago
class Efectivo(metodo_de_pago):
    def __init__(self, monto, recibo):
        super().__init__(monto)
        self.recibo= recibo
        
    def procesar_pago(self):
        super().procesar_pago()
        print(f"el monto es: {self.monto}, Recibo: {self.recibo}")