class Restaurante:
    def __init__(self, nombre, direccion, menu=None):
        self.nombre = nombre
        self.direccion = direccion
        self._menu = []        
        self._clientes = []   
        self._pedidos = []    
        if menu is not None:
            self.menu = menu
    @property
    def nombre(self):
        return self._nombre
    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or valor.strip() == "":
            raise ValueError("El nombre no puede estar vacío")
        self._nombre = valor.strip()
    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, valor):
        if not isinstance(valor, str) or valor.strip() == "":
            raise ValueError("La dirección no puede estar vacía")
        self._direccion = valor.strip()
    @property
    def menu(self):
        return list(self._menu)   

    @menu.setter
    def menu(self, productos):
        # Reemplaza el menú completo, sin nombres repetidos
        nombres = []
        for p in productos:
            if p.nombre.lower() in nombres:
                raise ValueError("Producto repetido en el menú: " + p.nombre)
            nombres.append(p.nombre.lower())
        self._menu = list(productos)

    @property
    def clientes(self):
        return list(self._clientes)  # devuelve una copia

    @property
    def pedidos(self):
        return list(self._pedidos)   # devuelve una copia

    # ---------- Métodos del diagrama ----------
    def listar_menu(self, dia):
        """Devuelve los productos disponibles en el día indicado."""
        disponibles = []
        for producto in self._menu:
            if producto.esta_disponible(dia):   # cada producto responde por sí mismo
                disponibles.append(producto)
        return disponibles
    def registrar_cliente(self, cliente):
        """Guarda un cliente (ya validado por la clase Cliente)."""
        for c in self._clientes:
            if c.telefono == cliente.telefono:
                raise ValueError("Ya existe un cliente con ese teléfono")
        self._clientes.append(cliente)
    def crear_pedido(self, clase_pedido, cliente, **datos):
        """
        Crea un pedido con la clase que se le pasa (PedidoLocal, PedidoParaLlevar
        o PedidoDelivery) y lo registra. Ejemplo:
            crear_pedido(PedidoLocal, cliente, mesa=3)
        """
        # Una mesa no puede tener dos pedidos abiertos
        mesa = datos.get("mesa")
        if mesa is not None:
            for pedido in self._pedidos:
                if pedido.esta_abierto() and pedido.ocupa_mesa(mesa):
                    raise ValueError("La mesa " + str(mesa) + " ya tiene un pedido abierto")
        numero = len(self._pedidos) + 1
        pedido = clase_pedido(numero, cliente, **datos)
        self.registrar_pedido(pedido)
        return pedido
    def registrar_pedido(self, pedido):
        """Guarda el pedido en la lista de pedidos."""
        self._pedidos.append(pedido)
    def reportar_ventas(self, fecha):
        """
        Ventas del día: total por tipo de pedido y los 3 productos más vendidos.
        Solo cuenta los pedidos ENTREGADOS en esa fecha.
        """
        ventas_por_tipo = {}   # tipo -> total en Bs
        cantidades = {}        # nombre del producto -> cantidad vendida
        for pedido in self._pedidos:
            if pedido.estado != "ENTREGADO" or pedido.fecha != fecha:
                continue
            tipo = pedido.tipo()    # cada pedido dice su tipo
            ventas_por_tipo[tipo] = ventas_por_tipo.get(tipo, 0) + pedido.calcular_total()
            for producto, cantidad in pedido.items:
                nombre = producto.nombre
                cantidades[nombre] = cantidades.get(nombre, 0) + cantidad
        # Pares (cantidad, nombre) ordenados de mayor a menor
        pares = []
        for nombre in cantidades:
            pares.append((cantidades[nombre], nombre))
        pares.sort(reverse=True)
        for tipo in ventas_por_tipo:
            ventas_por_tipo[tipo] = round(ventas_por_tipo[tipo], 2)
        return {
            "fecha": fecha,
            "ventas_por_tipo": ventas_por_tipo,
            "total_dia": round(sum(ventas_por_tipo.values()), 2),
            "top_3": pares[:3],
        }