# modelo/productos.py
from abc import ABC, abstractmethod

DIAS = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")


def validar_dia(dia):
    dia = dia.strip().lower().replace("é", "e").replace("á", "a")
    if dia not in DIAS:
        raise ValueError("Día no válido. Escriba un día de lunes a domingo.")
    return dia


class Producto(ABC):
    def __init__(self, nombre, precio_base, disponible=True):
        self.nombre = nombre
        self._precio_base = self.validar_precio(precio_base)
        self.disponible = disponible

    @staticmethod
    def validar_precio(precio):
        if precio <= 0:
            raise ValueError("El precio debe ser mayor que cero.")
        return round(precio, 2)

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def precio_base(self):
        return self._precio_base

    @precio_base.setter
    def precio_base(self, valor):
        self._precio_base = self.validar_precio(valor)

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = bool(valor)

    @abstractmethod
    def calcular_precio(self):
        pass

    @abstractmethod
    def esta_disponible(self, dia):
        pass

    @abstractmethod
    def contar_platos(self):
        pass

    def validar_disponibilidad(self, dia):
        if not self.esta_disponible(dia):
            raise ValueError(f"'{self.nombre}' no está disponible el día {dia}.")

    def aplica_2x1_martes(self):
        # Por defecto ningún producto entra en la promoción; Bebida lo sobrescribe
        return False

    def contiene(self, producto):
        # Un producto simple solo se contiene a sí mismo; Combo lo sobrescribe
        return self is producto

    def __str__(self):
        return f"{self.nombre} - Bs {self.calcular_precio():.2f}"


class Plato(Producto):
    def __init__(self, nombre, precio_base, disponible=True, solo_domingo=False):
        super().__init__(nombre, precio_base, disponible)
        self._solo_domingo = bool(solo_domingo)

    @property
    def solo_domingo(self):
        return self._solo_domingo

    def calcular_precio(self):
        return self.precio_base

    def obtener_precio(self):
        return self.calcular_precio()

    def esta_disponible(self, dia):
        dia = validar_dia(dia)
        if not self.disponible:
            return False
        if self._solo_domingo:
            return dia == "domingo"
        return True

    def contar_platos(self):
        return 1

    def __str__(self):
        texto = super().__str__()
        if self._solo_domingo:
            texto += " (solo domingos)"
        return texto


class Bebida(Producto):
    def __init__(self, nombre, precio_base, disponible=True, jarra=False, vaso=True, natural=True):
        super().__init__(nombre, precio_base, disponible)
        if jarra == vaso:
            raise ValueError("La bebida debe ser jarra o vaso (solo una de las dos).")
        self._jarra = bool(jarra)
        self._vaso = bool(vaso)
        self._natural = bool(natural)

    @property
    def natural(self):
        return self._natural

    def es_jarra(self):
        return self._jarra

    def es_vaso(self):
        return self._vaso

    def calcular_precio(self):
        # precio_base es el precio por vaso; la jarra cuesta 3 veces el vaso
        factor = 3 if self._jarra else 1
        return round(self.precio_base * factor, 2)

    def obtener_precio(self):
        return self.calcular_precio()

    def esta_disponible(self, dia):
        validar_dia(dia)
        return self.disponible

    def contar_platos(self):
        return 0

    def aplica_2x1_martes(self):
        # Variante B: solo vasos de refresco natural
        return self._natural and self._vaso

    def __str__(self):
        presentacion = "jarra" if self._jarra else "vaso"
        tipo = "natural" if self._natural else "gaseosa"
        return f"{self.nombre} ({presentacion}, {tipo}) - Bs {self.calcular_precio():.2f}"


class Combo(Producto):
    DESCUENTO = 12  # Variante B: 12 %

    def __init__(self, nombre, productos, disponible=True):
        if len(productos) < 2:
            raise ValueError("Un combo debe tener al menos 2 productos.")
        suma = sum(p.calcular_precio() for p in productos)
        super().__init__(nombre, suma, disponible)
        self._productos = []
        for producto in productos:
            self.agregar_producto(producto)

    @property
    def productos(self):
        return tuple(self._productos)

    @property
    def descuento(self):
        return self.DESCUENTO

    @property
    def precio_base(self):
        # La suma de los productos se recalcula siempre
        return round(sum(p.calcular_precio() for p in self._productos), 2)

    @property
    def precio_combo(self):
        return self.calcular_precio()

    def agregar_producto(self, producto):
        if producto.contiene(self):
            raise ValueError("Un combo no puede contenerse a sí mismo.")
        self._productos.append(producto)

    def quitar_producto(self, producto):
        if producto not in self._productos:
            raise ValueError("Ese producto no está en el combo.")
        if len(self._productos) <= 2:
            raise ValueError("Un combo debe tener al menos 2 productos.")
        self._productos.remove(producto)

    def calcular_precio(self):
        total = self.precio_base
        return round(total - total * self.DESCUENTO / 100, 2)

    def esta_disponible(self, dia):
        return self.disponible and all(p.esta_disponible(dia) for p in self._productos)

    def contar_platos(self):
        return sum(p.contar_platos() for p in self._productos)

    def contiene(self, producto):
        if self is producto:
            return True
        return any(p.contiene(producto) for p in self._productos)

    def __str__(self):
        nombres = ", ".join(p.nombre for p in self._productos)
        return f"COMBO {self.nombre} [{nombres}] - Bs {self.calcular_precio():.2f} (-12 %)"


class Promocion:
    """Variante B: los martes, 2 x 1 en vasos de refresco natural."""

    def __init__(self, dia="martes"):
        self.dia = validar_dia(dia)

    def es_aplicable(self, dia):
        return dia.strip().lower() == self.dia

    def aplicar_descuento(self, productos, dia):
        """Devuelve el descuento: de cada 2 vasos, el más barato es gratis."""
        if not self.es_aplicable(dia):
            return 0.0
        precios_vasos = []
        for p in productos:
            if p.aplica_2x1_martes():
                precios_vasos.append(p.calcular_precio())
        precios_vasos.sort(reverse=True)
        descuento = 0.0
        for i in range(1, len(precios_vasos), 2):
            descuento += precios_vasos[i]
        return round(descuento, 2)

    def contar_vasos(self, productos):
        """Devuelve (vasos entregados, vasos cobrados)."""
        entregados = 0
        for p in productos:
            if p.aplica_2x1_martes():
                entregados += 1
        cobrados = (entregados + 1) // 2
        return entregados, cobrados