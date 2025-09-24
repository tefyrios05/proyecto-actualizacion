import sqlite3
from tabulate import tabulate

DB_NAME = "productos.db"

def agregar_producto():
    print("\n--- NUEVO PRODUCTO ---")
    nombre = input("Nombre del producto: ").strip()
    if not nombre:
        print("El nombre es obligatorio.")
        return

    tipo = input("Tipo (ej: Lana, Hilo, Tela, Otro): ").strip()

    materiales = []  # Lista para guardar cada material ingresado

    while True:
        print("\n= AGREGAR MATERIAL =")
        print("1. Ingresar material")
        print("2. Calcular precio y guardar producto")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            nom_mat = input("Nombre del material: ").strip()
            opcion1 = input("*Si el material es en gramos presione 1, si es por unidades presione 2*: ").strip()

            if opcion1 == "1":
                gramos = float(input("Cantidad total de gramos del material: ").strip())
                precio_material = float(input("Precio total del material (Bs): ").strip())
                gramos_usados = float(input(f"Cantidad de gramos que se usará de '{nom_mat}' (máx {gramos}): ").strip())
                if gramos_usados > gramos:
                    gramos_usados = gramos
                materiales.append({
                    "nom_mat": nom_mat,
                    "tipo": "gramos",
                    "total": gramos,
                    "usado": gramos_usados,
                    "precio": precio_material
                })

            elif opcion1 == "2":
                unidades = float(input("Cantidad de unidades en la presentación: ").strip())
                precio_material = float(input("Precio total del material (Bs): ").strip())
                unidades_usadas = float(input(f"Cantidad de unidades que se usará de '{nom_mat}' (máx {unidades}): ").strip())
                if unidades_usadas > unidades:
                    unidades_usadas = unidades
                materiales.append({
                    "nom_mat": nom_mat,
                    "tipo": "unidades",
                    "total": unidades,
                    "usado": unidades_usadas,
                    "precio": precio_material
                })
            else:
                print("Opción inválida, vuelva a intentar.")

        elif opcion == "2":
            tiempo = float(input("Tiempo de elaboración (horas): ").strip())
            tarifa_por_hora = float(input("Tarifa por hora (Bs): ").strip())

            total_material = 0
            detalle_materiales = []

            # Calcular costo total de todos los materiales
            for mat in materiales:
                if mat["tipo"] == "gramos":
                    costo_por_gramo = mat["precio"] / mat["total"]
                    costo_usado = costo_por_gramo * mat["usado"]
                    total_material += costo_usado
                    detalle_materiales.append(f"{mat['nom_mat']} ({mat['usado']} g): {costo_usado:.2f} Bs")
                else:
                    costo_por_unidad = mat["precio"] / mat["total"]
                    costo_usado = costo_por_unidad * mat["usado"]
                    total_material += costo_usado
                    detalle_materiales.append(f"{mat['nom_mat']} ({mat['usado']} unid): {costo_usado:.2f} Bs")

            costo_mano_obra = tiempo * tarifa_por_hora
            total = total_material + costo_mano_obra

            # Guardar en la base de datos
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO productos (nombre, precio, tiempo, tipo, gramos, materiales_unidad, nom_mat)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre, total, tiempo, tipo,
                sum([m["usado"] for m in materiales if m["tipo"]=="gramos"]),
                sum([m["usado"] for m in materiales if m["tipo"]=="unidades"]),
                ", ".join([m["nom_mat"] for m in materiales])
            ))
            conn.commit()
            conn.close()

            print(f"\n✅ Producto '{nombre}' agregado correctamente.")
            print("Detalle de materiales usados:")
            for det in detalle_materiales:
                print(f"  - {det}")
            print(f"Mano de obra: {costo_mano_obra:.2f} Bs")
            print(f"PRECIO TOTAL: {total:.2f} Bs")
            break

        else:
            print("Opción no válida. Intente de nuevo.")

def ver_productos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nombre, tipo, nom_mat, precio, tiempo, gramos, materiales_unidad, created_at FROM productos ORDER BY id")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        print("Error: La columna 'created_at' no existe. Por favor, actualiza la base de datos.")
        conn.close()
        return
    conn.close()

    if not rows:
        print("\nNo hay productos registrados.")
        return

    tabla = []
    for row in rows:
        pid, nombre, tipo, nom_mat, precio, tiempo, gramos, mat_unid, created = row
        precio_por_unidad = precio / mat_unid if mat_unid > 0 else 0
        precio_por_gramo = precio / gramos if gramos > 0 else 0
        cobro_por_hora = precio / tiempo if tiempo > 0 else 0
        tabla.append([pid, nombre, tipo, nom_mat, f"{precio:.2f}", f"{tiempo:.2f}", gramos, mat_unid,
                      round(precio_por_unidad,2), round(precio_por_gramo,2), round(cobro_por_hora,2), created])

    headers = ["ID", "Nombre", "Tipo", "Material", "Precio (Bs)", "Tiempo (h)", "Gramos",
               "Mat/pres", "Precio/unid", "Precio/gramo", "Cobro/hora", "Creado"]
    print("\n=== LISTA DE PRODUCTOS ===")
    print(tabulate(tabla, headers=headers, tablefmt="grid"))

    sel = input("\nIngrese ID para ver detalle (ENTER para volver): ").strip()
    if sel == "":
        return
    try:
        pid = int(sel)
    except:
        print("ID inválido.")
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT nombre, tipo, nom_mat, precio, tiempo, gramos, materiales_unidad, created_at FROM productos WHERE id = ?", (pid,))
    prod = cur.fetchone()
    conn.close()
    if not prod:
        print("Producto no encontrado.")
        return

    nombre, tipo, nom_mat, precio, tiempo, gramos, mat_unid, created = prod
    print(f"\nDETALLE PRODUCTO: {nombre} (ID {pid})")
    print(f"Tipo: {tipo}")
    print(f"Material registrado: {nom_mat}")
    print(f"Tiempo: {tiempo} h")
    print(f"Precio total: {precio:.2f} Bs")
    if gramos > 0:
        print(f"Gramos usados: {gramos}")
        print(f"Precio por gramo aproximado: {precio/gramos:.4f} Bs/gr")
    if mat_unid > 0:
        print(f"Presentación unidades: {mat_unid}")

def menu():
    while True:
        print("\n===== MENU PRINCIPAL =====")
        print("1. Nuevo producto")
        print("2. Ver productos")
        print("3. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            agregar_producto()
        elif opcion == "2":
            ver_productos()
        elif opcion == "3":
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()
