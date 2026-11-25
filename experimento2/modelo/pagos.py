# modelo/pagos.py
from abc import ABC, abstractmethod


class MetodoPago(ABC):
    def __init__(self, monto):
        self.monto = monto

    @property
    def monto(self):
        return self._monto

    @monto.setter
    def monto(self, valor):
        if valor <= 0:
            raise ValueError("El monto debe ser mayor que cero.")
        self._monto = round(valor, 2)

    def permitido_en_delivery(self):
        # Efectivo y QR se aceptan en delivery; Tarjeta lo sobrescribe
        return True

    @abstractmethod
    def procesar_pago(self):
        pass


class Efectivo(MetodoPago):
    def __init__(self, monto, recibo):
        super().__init__(monto)
        self._recibo = round(recibo, 2)  # dinero que entrega el cliente

    @property
    def recibo(self):
        return self._recibo

    def calcular_cambio(self):
        return round(self._recibo - self.monto, 2)

    def procesar_pago(self):
        if self._recibo < self.monto:
            raise ValueError(f"El efectivo (Bs {self._recibo:.2f}) no cubre el total (Bs {self.monto:.2f}).")
        return (f"Pago en EFECTIVO | Total: Bs {self.monto:.2f} | "
                f"Recibido: Bs {self._recibo:.2f} | Cambio: Bs {self.calcular_cambio():.2f}")


class Qr(MetodoPago):
    def __init__(self, monto, codigo):
        super().__init__(monto)
        self.codigo = codigo

    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, valor):
        valor = str(valor).strip()
        if len(valor) != 10 or not valor.isdigit():
            raise ValueError("El código QR debe tener 10 dígitos.")
        self._codigo = valor

    def procesar_pago(self):
        return f"Pago con QR | Total: Bs {self.monto:.2f} | Código: {self.codigo}"


class Tarjeta(MetodoPago):
    COMISION = 3  # 3 % a cargo del cliente

    def __init__(self, monto, numero_tarjeta):
        super().__init__(monto)
        numero_tarjeta = str(numero_tarjeta).strip()
        if not numero_tarjeta.isdigit():
            raise ValueError("El número de tarjeta solo debe tener dígitos.")
        self._numero_tarjeta = numero_tarjeta

    @property
    def numero_tarjeta(self):
        return self._numero_tarjeta

    @property
    def comision(self):
        return self.COMISION

    def calcular_comision(self):
        return round(self.monto * self.COMISION / 100, 2)

    def permitido_en_delivery(self):
        return False

    def procesar_pago(self):
        total = round(self.monto + self.calcular_comision(), 2)
        return (f"Pago con TARJETA ****{self._numero_tarjeta[-4:]} | Pedido: Bs {self.monto:.2f} | "
                f"Comisión 3 %: Bs {self.calcular_comision():.2f} | Total cobrado: Bs {total:.2f}")