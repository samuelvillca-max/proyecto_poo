from modelo.pedidos import PedidoLocal, PedidoParaLlevar, PedidoDelivery


class Restaurante:
    def __init__(self, nombre="Sabor Valluno", direccion="Cochabamba"):
        self._nombre = nombre
        self._direccion = direccion
        self._menu = []
        self._clientes = []
        self._pedidos = []

    @property
    def nombre(self):
        return self._nombre

    @property
    def direccion(self):
        return self._direccion

    @property
    def menu(self):
        return list(self._menu)

    @property
    def clientes(self):
        return list(self._clientes)

    @property
    def pedidos(self):
        return list(self._pedidos)

    def agregar_al_menu(self, producto):
        self._menu.append(producto)

    def listar_menu(self, dia):
        return [p for p in self._menu if p.esta_disponible(dia)]

    def registrar_cliente(self, cliente):
        if self.buscar_cliente(cliente.telefono) is not None:
            raise ValueError("Ya existe un cliente con ese teléfono.")
        self._clientes.append(cliente)

    def buscar_cliente(self, telefono):
        for cliente in self._clientes:
            if cliente.telefono == telefono:
                return cliente
        return None

    def mesa_ocupada(self, mesa):
        for pedido in self._pedidos:
            if pedido.TIPO == "local" and pedido.mesa == mesa and \
                    pedido.estado not in ("ENTREGADO", "CANCELADO"):
                return True
        return False

    def crear_pedido(self, tipo, cliente, dia, mesa=0, direccion="", zona=""):
        numero = len(self._pedidos) + 1
        if tipo == "1":
            if self.mesa_ocupada(mesa):
                raise ValueError(f"La mesa {mesa} ya tiene un pedido abierto.")
            pedido = PedidoLocal(numero, cliente, mesa, dia=dia)
        elif tipo == "2":
            pedido = PedidoParaLlevar(numero, cliente, dia=dia)
        else:
            pedido = PedidoDelivery(numero, cliente, direccion, zona, dia=dia)
        return pedido

    def registrar_pedido(self, pedido):
        self._pedidos.append(pedido)
        pedido.cliente.realizar_pedido(pedido)

    def reportar_ventas(self):
        """Devuelve las ventas por tipo de pedido y los 3 productos más vendidos."""
        por_tipo = {"local": [0, 0.0], "para llevar": [0, 0.0], "delivery": [0, 0.0]}
        unidades = {}
        for pedido in self._pedidos:
            if pedido.pago is None or pedido.estado == "CANCELADO":
                continue
            por_tipo[pedido.TIPO][0] += 1
            por_tipo[pedido.TIPO][1] += pedido.calcular_total()
            for producto in pedido.productos:
                unidades[producto.nombre] = unidades.get(producto.nombre, 0) + 1
        ranking = sorted(unidades.items(), key=lambda par: par[1], reverse=True)
        return por_tipo, ranking[:3]