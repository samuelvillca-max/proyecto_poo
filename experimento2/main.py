# main.py
from restaurante import Restaurante
from modelo.clientes import Cliente
from modelo.productos import Plato, Bebida, Combo, validar_dia
from modelo.pagos import Efectivo, Qr, Tarjeta

restaurante = Restaurante()

def pedir_texto(mensaje):
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("  No puede quedar vacío.")


def pedir_numero(mensaje):
    while True:
        try:
            return float(input(mensaje).replace(",", "."))
        except ValueError:
            print("  Ingrese un número válido.")


def pedir_entero(mensaje):
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("  Ingrese un número entero.")


def pedir_si_no(mensaje):
    while True:
        respuesta = input(mensaje + " (s/n): ").strip().lower()
        if respuesta in ("s", "n"):
            return respuesta == "s"
        print("  Responda s o n.")


def pedir_dia(mensaje):
    while True:
        try:
            return validar_dia(input(mensaje))
        except ValueError as error:
            print(f"  {error}")


def elegir_producto(productos):
    for i, p in enumerate(productos, start=1):
        print(f"  {i}. {p}")
    print("  0. Terminar")
    opcion = pedir_entero("Elija un producto: ")
    if 1 <= opcion <= len(productos):
        return productos[opcion - 1]
    return None


def registrar_plato():
    nombre = pedir_texto("Nombre del plato: ")
    precio = pedir_numero("Precio (Bs): ")
    disponible = pedir_si_no("¿Está disponible?")
    solo_domingo = pedir_si_no("¿Se vende solo los domingos?")
    restaurante.agregar_al_menu(Plato(nombre, precio, disponible, solo_domingo))
    print("Plato registrado.")


def registrar_bebida():
    nombre = pedir_texto("Nombre de la bebida: ")
    precio = pedir_numero("Precio por vaso (Bs): ")
    disponible = pedir_si_no("¿Está disponible?")
    natural = pedir_si_no("¿Es refresco natural? (n = gaseosa)")
    es_jarra = pedir_si_no("¿Es jarra? (n = vaso)")
    bebida = Bebida(nombre, precio, disponible, jarra=es_jarra, vaso=not es_jarra, natural=natural)
    restaurante.agregar_al_menu(bebida)
    print(f"Bebida registrada: {bebida}")


def registrar_combo():
    nombre = pedir_texto("Nombre del combo: ")
    elegidos = []
    print("Elija al menos 2 productos (0 para terminar):")
    while True:
        producto = elegir_producto(restaurante.menu)
        if producto is None:
            break
        elegidos.append(producto)
        print(f"  + {producto.nombre}")
    combo = Combo(nombre, elegidos)
    restaurante.agregar_al_menu(combo)
    print(f"Combo registrado: {combo}")


def ver_menu_del_dia():
    dia = pedir_dia("Día de la semana: ")
    productos = restaurante.listar_menu(dia)
    print(f"\n--- Menú del {dia} ---")
    if not productos:
        print("  No hay productos disponibles.")
    for p in productos:
        print(f"  - {p}")
    if dia == "martes":
        print("  ¡Hoy 2 x 1 en vasos de refresco natural!")


def mostrar_menu():
    while True:
        print("\n----- MENÚ DEL RESTAURANTE -----")
        print("1. Ver menú de un día")
        print("2. Registrar plato")
        print("3. Registrar bebida")
        print("4. Registrar combo")
        print("0. Volver")
        opcion = input("Opción: ").strip()
        try:
            if opcion == "1":
                ver_menu_del_dia()
            elif opcion == "2":
                registrar_plato()
            elif opcion == "3":
                registrar_bebida()
            elif opcion == "4":
                registrar_combo()
            elif opcion == "0":
                return
            else:
                print("Opción no válida.")
        except ValueError as error:
            print(f"Error: {error}")

def cobrar(pedido):
    print("Método de pago: 1. Efectivo  2. QR  3. Tarjeta")
    opcion = input("Opción: ").strip()
    total = pedido.calcular_total()
    if opcion == "1":
        metodo = Efectivo(total, pedir_numero(f"¿Con cuánto paga? (total Bs {total:.2f}): "))
    elif opcion == "2":
        metodo = Qr(total, pedir_texto("Código QR (10 dígitos): "))
    else:
        metodo = Tarjeta(total, pedir_texto("Número de tarjeta: "))
    comprobante = pedido.pagar(metodo)  # si el pago no es válido, lanza el error aquí
    print("\n========== COMPROBANTE ==========")
    print(pedido.detalle())
    print(comprobante)
    print("=================================")


def realizar_pedido(cliente):
    print("Tipo de pedido: 1. Local  2. Para llevar  3. Delivery")
    tipo = input("Opción: ").strip()
    if tipo not in ("1", "2", "3"):
        print("Tipo no válido.")
        return
    dia = pedir_dia("Día del pedido: ")
    mesa, direccion, zona = 0, "", ""
    if tipo == "1":
        mesa = pedir_entero("Número de mesa (1 a 15): ")
    elif tipo == "3":
        direccion = pedir_texto("Dirección: ")
        zona = pedir_texto("Zona (Cercado, Quillacollo, Sacaba, Vinto): ")
    pedido = restaurante.crear_pedido(tipo, cliente, dia, mesa, direccion, zona)

    disponibles = restaurante.listar_menu(dia)
    if not disponibles:
        print("No hay productos disponibles ese día. Registre productos primero.")
        return
    while True:
        producto = elegir_producto(disponibles)
        if producto is None:
            if not pedido.productos:
                print("Pedido cancelado: no tiene productos.")
                return
            try:
                print("\n" + pedido.detalle())
                break
            except ValueError as error:  # por ejemplo, no llega al mínimo de delivery
                print(f"Error: {error}")
                if not pedir_si_no("¿Desea agregar más productos?"):
                    return
                continue
        cantidad = pedir_entero("Cantidad (1 a 20): ")
        try:
            pedido.agregar_producto(producto, cantidad)
        except ValueError as error:
            print(f"Error: {error}")

    restaurante.registrar_pedido(pedido)
    if pedir_si_no("¿Desea pagar ahora?"):
        while True:
            try:
                cobrar(pedido)
                break
            except ValueError as error:
                print(f"Error: {error}")
                if not pedir_si_no("¿Intentar con otro pago?"):
                    break


def registrar_cliente():
    while True:
        telefono = pedir_texto("Teléfono (8 dígitos, empieza en 6 o 7): ")
        if Cliente.validar_telefono(telefono):
            break
        print("  Teléfono inválido: debe tener 8 dígitos y comenzar con 6 o 7.")
    cliente = restaurante.buscar_cliente(telefono)
    if cliente is not None:
        print(f"Cliente ya registrado: {cliente}")
    else:
        nombre = pedir_texto("Nombre: ")
        cliente = Cliente(nombre, telefono)
        restaurante.registrar_cliente(cliente)
        print(f"Cliente registrado: {cliente}")
    if pedir_si_no("¿Desea realizar un pedido?"):
        realizar_pedido(cliente)

def reporte_ventas():
    por_tipo, mas_vendidos = restaurante.reportar_ventas()
    print("\n----- REPORTE DE VENTAS (pedidos pagados) -----")
    total = 0.0
    for tipo, (cantidad, monto) in por_tipo.items():
        print(f"  {tipo:<12}: {cantidad} pedido(s) - Bs {monto:.2f}")
        total += monto
    print(f"  TOTAL       : Bs {total:.2f}")
    print("Los 3 productos más vendidos:")
    if not mas_vendidos:
        print("  Todavía no hay ventas.")
    for i, (nombre, unidades) in enumerate(mas_vendidos, start=1):
        print(f"  {i}. {nombre} - {unidades} unidad(es)")

def main():
    while True:
        print("\n========== SABOR VALLUNO ==========")
        print("1. Mostrar menú")
        print("2. Registrar cliente")
        print("3. Reporte de ventas")
        print("4. Salir")
        opcion = input("Opción: ").strip()
        try:
            if opcion == "1":
                mostrar_menu()
            elif opcion == "2":
                registrar_cliente()
            elif opcion == "3":
                reporte_ventas()
            elif opcion == "4":
                print("¡Hasta pronto!")
                break
            else:
                print("Opción no válida.")
        except ValueError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()