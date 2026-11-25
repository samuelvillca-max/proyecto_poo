class Producto:
    def __init__(self, nombre, precio_base, disponible):
        self.nombre = nombre
        self.precio_base = precio_base
        self.disponible = disponible
    def calcular_precio(self):
        return self.precio_base
    def esta_disponible(self):
        return self.disponible
    def validar_disponibilidad(self):
        return self.esta_disponible()

class Plato(Producto):
    def __init__(self, nombre, precio_base, disponible, solo_domingo):
        super().__init__(nombre, precio_base, disponible)
        self.solo_domingo = solo_domingo
    def esta_disponible(self):
        return self.disponible
    def obtener_precio(self):
        return self.calcular_precio()

class Bebida(Producto):
    def __init__(self, nombre, precio_base, disponible, jarra, vaso):
        super().__init__(nombre, precio_base, disponible)
        self.jarra = jarra
        self.vaso = vaso
    def obtener_precio(self):
        return self.calcular_precio()
    def es_jarra(self):
        return self.jarra
    def es_vaso(self):
        return self.vaso

class Combo:
    def __init__(self, descuento=0):
        self.productos = []
        self.descuento = descuento
        self.precio_combo = 0
    def agregar_producto(self, producto):
        self.productos.append(producto)
    def quitar_producto(self, producto):
        self.productos.remove(producto)
    def calcular_precio(self):
        total = sum(p.calcular_precio() for p in self.productos)
        self.precio_combo = total - (total * self.descuento / 100)
        return self.precio_combo
    def esta_disponible(self):
        return all(p.esta_disponible() for p in self.productos)

class Promocion:
    def __init__(self, dia):
        self.dia = dia
    def aplicar_descuento(self, combo):
        if self.es_aplicable(combo):
            return combo.calcular_precio()
        return None
    def es_aplicable(self, combo):
        return self.dia(combo)