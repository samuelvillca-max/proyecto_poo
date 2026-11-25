# modelo/pedidos.py
from abc import ABC, abstractmethod

from modelo.productos import Promocion

ESTADOS_VALIDOS = ("REGISTRADO", "EN_PREPARACION", "LISTO", "ENTREGADO", "CANCELADO")


class Pedido(ABC):
    TIPO = "pedido"

    def __init__(self, numero, cliente, productos=None, estado="REGISTRADO", fecha="", dia=""):
        if numero <= 0:
            raise ValueError("El número de pedido debe ser mayor a 0.")
        if estado not in ESTADOS_VALIDOS:
            raise ValueError("Estado no válido.")

        self._numero = numero
        self._cliente = cliente
        self._fecha = fecha
        self._dia = dia.strip().lower()
        self._estado = estado
        self._productos = []
        self._pago = None
        self._promocion = Promocion("martes")

        if productos is not None:
            for p in productos:
                self._productos.append(p)

    @property
    def numero(self):
        return self._numero

    @property
    def cliente(self):
        return self._cliente

    @property
    def fecha(self):
        return self._fecha

    @property
    def productos(self):
        return list(self._productos)

    @property
    def pago(self):
        return self._pago

    @property
    def dia(self):
        return self._dia

    @dia.setter
    def dia(self, valor):
        self._dia = valor.strip().lower()

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, nuevo_estado):
        if nuevo_estado not in ESTADOS_VALIDOS:
            raise ValueError("Estado no válido.")

        if nuevo_estado == self._estado:
            return

        if self._estado == "REGISTRADO":
            if nuevo_estado != "EN_PREPARACION" and nuevo_estado != "CANCELADO":
                raise ValueError("Desde REGISTRADO solo puede pasar a EN_PREPARACION o CANCELADO.")
        elif self._estado == "EN_PREPARACION":
            if nuevo_estado != "LISTO":
                raise ValueError("Desde EN_PREPARACION solo puede pasar a LISTO.")
        elif self._estado == "LISTO":
            if nuevo_estado != "ENTREGADO":
                raise ValueError("Desde LISTO solo puede pasar a ENTREGADO.")
        elif self._estado == "ENTREGADO" or self._estado == "CANCELADO":
            raise ValueError("Un pedido ENTREGADO o CANCELADO ya no puede cambiar de estado.")

        self._estado = nuevo_estado

    def agregar_producto(self, producto, cantidad=1):
        if self._estado != "REGISTRADO":
            raise ValueError("Solo se pueden agregar productos cuando el pedido está REGISTRADO.")
        if cantidad < 1 or cantidad > 20:
            raise ValueError("La cantidad debe estar entre 1 y 20.")

        cantidad_actual = 0
        for p in self._productos:
            if p == producto:
                cantidad_actual += 1

        if cantidad_actual + cantidad > 20:
            raise ValueError("No se puede superar el máximo de 20 unidades por producto.")

        if self._dia != "":
            producto.validar_disponibilidad(self._dia)

        for _ in range(cantidad):
            self._productos.append(producto)

    def quitar_producto(self, producto):
        if self._estado != "REGISTRADO":
            raise ValueError("Solo se pueden quitar productos cuando el pedido está REGISTRADO.")
        if producto not in self._productos:
            raise ValueError("El producto no se encuentra en este pedido.")
        self._productos.remove(producto)

    def calcular_descuento_promocion(self):
        return self._promocion.aplicar_descuento(self._productos, self._dia)

    def calcular_subtotal(self):
        subtotal = 0.0
        for p in self._productos:
            subtotal += p.calcular_precio()
        subtotal -= self.calcular_descuento_promocion()
        return round(subtotal, 2)

    @abstractmethod
    def calcular_total(self):
        pass

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado

    def pagar(self, metodo_pago):
        if self._estado == "CANCELADO":
            raise ValueError("No se puede pagar un pedido cancelado.")
        if self._pago is not None:
            raise ValueError("Este pedido ya fue pagado.")
        if len(self._productos) == 0:
            raise ValueError("El pedido no tiene productos.")
        metodo_pago.monto = self.calcular_total()
        comprobante = metodo_pago.procesar_pago()
        self._pago = metodo_pago
        return comprobante

    def detalle(self):
        lineas = [f"Pedido N.º {self._numero} ({self.TIPO}) - {self._cliente.nombre} - "
                  f"Día: {self._dia} - Estado: {self._estado}"]
        contados = []
        for p in self._productos:
            if p not in contados:
                contados.append(p)
                cantidad = self._productos.count(p)
                lineas.append(f"  {cantidad} x {p}")
        descuento = self.calcular_descuento_promocion()
        if descuento > 0:
            entregados, cobrados = self._promocion.contar_vasos(self._productos)
            lineas.append(f"  Promo martes 2 x 1: -Bs {descuento:.2f} "
                          f"(vasos entregados {entregados}, cobrados {cobrados})")
        subtotal = self.calcular_subtotal()
        total = self.calcular_total()
        lineas.append(f"  Subtotal: Bs {subtotal:.2f}")
        lineas.append(f"  Cargos ({self.TIPO}): Bs {total - subtotal:.2f}")
        lineas.append(f"  TOTAL: Bs {total:.2f}")
        return "\n".join(lineas)


class PedidoLocal(Pedido):
    TIPO = "local"

    def __init__(self, numero, cliente, mesa, productos=None, estado="REGISTRADO", fecha="", dia=""):
        super().__init__(numero, cliente, productos, estado, fecha, dia)
        self._mesa = 0
        self.mesa = mesa

    @property
    def mesa(self):
        return self._mesa

    @mesa.setter
    def mesa(self, valor):
        if valor < 1 or valor > 15:
            raise ValueError("El número de mesa debe estar entre 1 y 15.")
        self._mesa = valor

    def calcular_total(self):
        return self.calcular_subtotal()


class PedidoParaLlevar(Pedido):
    TIPO = "para llevar"

    def __init__(self, numero, cliente, costo_envase=2.50, productos=None, estado="REGISTRADO", fecha="", dia=""):
        super().__init__(numero, cliente, productos, estado, fecha, dia)
        self._costo_envase = 0.0
        self.costo_envase = costo_envase

    @property
    def costo_envase(self):
        return self._costo_envase

    @costo_envase.setter
    def costo_envase(self, valor):
        if valor < 0:
            raise ValueError("El costo del envase no puede ser negativo.")
        self._costo_envase = round(valor, 2)

    def contar_platos(self):
        total_platos = 0
        for p in self._productos:
            total_platos += p.contar_platos()
        return total_platos

    def calcular_total(self):
        subtotal = self.calcular_subtotal()
        total_envases = self.contar_platos() * self._costo_envase
        return round(subtotal + total_envases, 2)


class PedidoDelivery(Pedido):
    TIPO = "delivery"
    TARIFAS = {"cercado": 8.0, "quillacollo": 15.0, "sacaba": 15.0, "vinto": 20.0}
    ENVIO_GRATIS_DESDE = 120.0

    def __init__(
        self,
        numero,
        cliente,
        direccion,
        zona,
        zona_gratis="Todas",
        minimo_delivery=50.0,
        productos=None,
        estado="REGISTRADO",
        fecha="",
        dia="",
    ):
        super().__init__(numero, cliente, productos, estado, fecha, dia)
        self._direccion = ""
        self._zona = ""
        self._costo_envio = 0.0
        self._zona_gratis = zona_gratis
        self._minimo_delivery = minimo_delivery

        self.direccion = direccion
        self.zona = zona

    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, valor):
        if not valor or not valor.strip():
            raise ValueError("La dirección no puede estar vacía.")
        self._direccion = valor.strip()

    @property
    def zona(self):
        return self._zona

    @zona.setter
    def zona(self, valor):
        zona_limpia = valor.strip().lower()
        if zona_limpia not in self.TARIFAS:
            raise ValueError("Zona no válida. Debe ser: Cercado, Quillacollo, Sacaba o Vinto.")
        self._zona = zona_limpia.capitalize()
        self._costo_envio = self.TARIFAS[zona_limpia]

    @property
    def zona_gratis(self):
        return self._zona_gratis

    @property
    def minimo_delivery(self):
        return self._minimo_delivery

    @property
    def costo_envio(self):
        return self._costo_envio

    def ver_zona(self):
        return self._zona

    def validar_minimo(self):
        return self.calcular_subtotal() >= self._minimo_delivery

    def calcular_total(self):
        subtotal = self.calcular_subtotal()
        if not self.validar_minimo():
            raise ValueError(f"El pedido no alcanza el monto mínimo de delivery (Bs {self._minimo_delivery:.2f}).")
        if subtotal >= self.ENVIO_GRATIS_DESDE:
            return subtotal
        return round(subtotal + self._costo_envio, 2)

    def pagar(self, metodo_pago):
        if not metodo_pago.permitido_en_delivery():
            raise ValueError("Los pedidos por delivery solo aceptan pago en Efectivo o QR.")
        return super().pagar(metodo_pago)