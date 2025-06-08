# src/logica/gestor_stock.py
from tkinter import messagebox, Tk
import datetime
import customtkinter as ctk  # Para el diálogo personalizado
from datos.conexion_bd import ConexionBD
from mysql.connector import Error
from utils.utilidades import Utilidades


class TripleOptionDialog(ctk.CTkToplevel):
    """
    Diálogo modal con tres opciones: "Atrás", "Actualizar" y "Continuar".
    Se usa cuando, para un producto con el mismo lote y la misma fecha de ingreso,
    el vencimiento ingresado es distinto al vencimiento ya registrado.
    
    La respuesta se almacena en self.result:
      - "atras": se cancela la operación.
      - "actualizar": se actualizarán todos los registros de ese producto, lote y fecha,
         modificando el vencimiento al nuevo y sumando stock.
      - "continuar": se insertará un nuevo registro usando la fecha vigente (la ya registrada).
    """
    def __init__(self, parent, mensaje):
        super().__init__(parent)
        self.title("Conflicto de Vencimiento")
        self.result = None
        self.grab_set()
        self.geometry("400x200")
        self.resizable(False, False)

        ctk.CTkLabel(self, text=mensaje, wraplength=380, justify="center").pack(padx=10, pady=20)

        frame_buttons = ctk.CTkFrame(self)
        frame_buttons.pack(pady=10)

        btn_atras = ctk.CTkButton(frame_buttons, text="Atrás", command=lambda: self._cerrar("atras"))
        btn_atras.grid(row=0, column=0, padx=5)

        btn_actualizar = ctk.CTkButton(frame_buttons, text="Actualizar", command=lambda: self._cerrar("actualizar"))
        btn_actualizar.grid(row=0, column=1, padx=5)

        btn_continuar = ctk.CTkButton(frame_buttons, text="Continuar", command=lambda: self._cerrar("continuar"))
        btn_continuar.grid(row=0, column=2, padx=5)

        self.protocol("WM_DELETE_WINDOW", lambda: self._cerrar("atras"))
        self.wait_window()

    def _cerrar(self, resultado):
        self.result = resultado
        self.destroy()


class StockManager:
    """
    Clase que maneja la lógica para la gestión de productos y lotes.

    Se espera que el diccionario "producto" contenga, además de "nombre", "precio" y "stock",
    las claves "lote" (identificador del lote) y "vencimiento" (fecha en formato "YYYY-MM-DD").

    Requiere que la tabla "productos" tenga un campo adicional "activo"
    (1 = activo, 0 = inactivo).
    """
    def agregar_o_actualizar_producto(self, producto) -> bool:
        """
        Agrega o actualiza un producto y registra el lote correspondiente.
        
        Primero se verifica si ya existe un producto con ese nombre (sin distinguir mayúsculas):
          - Si existe y está activo, se actualiza sumándole el nuevo stock.
          - Si existe pero está inactivo, se pregunta al usuario si desea reactivarlo.
            En ese caso se actualiza la fila existente, pero se reinicia el stock (la nueva cantidad)
            para que no se mezclen las cantidades anteriores con la nueva.
          - Si no existe, se crea un nuevo registro (con activo = 1).
        
        Luego se gestiona el registro en la tabla "lotes_productos":
          Se valida que para ese producto, número de lote y fechaIngreso = CURDATE() se use
          el registro existente; de lo contrario se inserta uno nuevo. Además, si ya existe un
          registro para ese grupo y el vencimiento ingresado es distinto al registrado, se muestra
          el diálogo de triple opción.
        
        Retorna True si la operación es exitosa, False en caso contrario.
        """
        if producto.get("stock") in (None, ""):
            messagebox.showerror("Error", "El campo 'Stock' es obligatorio.", parent=None)
            return False
        if not producto.get("vencimiento"):
            messagebox.showerror("Error", "El campo 'Fecha de vencimiento' es obligatorio.", parent=None)
            return False
        if not Utilidades.validar_producto(None, producto):
            return False

        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return False
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE ventas_db")

            # Buscar si existe un producto (sin distinguir mayúsculas), incluyendo la columna "activo"
            sql_busqueda = "SELECT prodId, stock, activo FROM productos WHERE LOWER(nombre) = LOWER(%s)"
            cursor.execute(sql_busqueda, (producto["nombre"],))
            resultado = cursor.fetchone()

            if resultado:
                if resultado["activo"] == 1:
                    # Producto activo: sumar stock
                    nuevo_stock = resultado["stock"] + producto["stock"]
                    sql_update = "UPDATE productos SET stock = %s, precio = %s WHERE prodId = %s"
                    cursor.execute(sql_update, (nuevo_stock, producto["precio"], resultado["prodId"]))
                    prodId = resultado["prodId"]
                else:
                    # Producto inactivo: preguntar si se desea reactivar (no se suma stock a la antigua información).
                    confirmacion = messagebox.askyesno(
                        "Reactivar producto",
                        "Se encontró un registro inactivo para este producto. ¿Deseas reactivarlo y reiniciar el stock con el nuevo valor?",
                        parent=None
                    )
                    if confirmacion:
                        # Reactivar el producto, estableciendo el nuevo stock (no sumando el antiguo)
                        sql_reactivar = "UPDATE productos SET stock = %s, precio = %s, activo = 1 WHERE prodId = %s"
                        cursor.execute(sql_reactivar, (producto["stock"], producto["precio"], resultado["prodId"]))
                        prodId = resultado["prodId"]
                    else:
                        # Si el usuario decide no reactivar, se inserta un nuevo registro (con un nuevo ID)
                        sql_insert = "INSERT INTO productos (nombre, precio, stock, activo) VALUES (%s, %s, %s, 1)"
                        cursor.execute(sql_insert, (producto["nombre"], producto["precio"], producto["stock"]))
                        prodId = cursor.lastrowid
            else:
                # No existe; se inserta un nuevo producto (activo)
                sql_insert = "INSERT INTO productos (nombre, precio, stock, activo) VALUES (%s, %s, %s, 1)"
                cursor.execute(sql_insert, (producto["nombre"], producto["precio"], producto["stock"]))
                prodId = cursor.lastrowid

            # Ahora procesamos la tabla "lotes_productos"
            # Se verifica si ya existe un registro para este producto, mismo número de lote, y con fechaIngreso = CURDATE()
            lote_valor = producto.get("lote", "")
            sql_verificar_lote = """
                SELECT loteID, vencimiento, cantidad_ingresada, cantidad_disponible
                FROM lotes_productos
                WHERE prodId = %s AND numeroLote = %s AND fechaIngreso = CURDATE()
                LIMIT 1
            """
            cursor.execute(sql_verificar_lote, (prodId, lote_valor))
            registro_lote = cursor.fetchone()

            cantidad = producto["stock"]
            nuevo_vencimiento = producto.get("vencimiento", None)

            if registro_lote:
                # Convertir el vencimiento registrado a cadena
                vencimiento_existente = registro_lote["vencimiento"]
                if isinstance(vencimiento_existente, (datetime.date, datetime.datetime)):
                    vencimiento_existente_str = vencimiento_existente.isoformat()
                else:
                    vencimiento_existente_str = str(vencimiento_existente)
            else:
                vencimiento_existente_str = None

            nuevo_vencimiento_str = str(nuevo_vencimiento)

            if registro_lote:
                if nuevo_vencimiento_str != vencimiento_existente_str:
                    # Si las fechas son distintas, se muestra el diálogo de triple opción.
                    mensaje_conflicto = (
                        f"El lote '{lote_valor}' ya existe con vencimiento {vencimiento_existente_str}.\n\n"
                        f"¿Deseas actualizar la fecha de vencimiento a la nueva ingresada ({nuevo_vencimiento_str}) "
                        "o continuar usando la fecha vigente?"
                    )
                    import tkinter as tk
                    if tk._default_root is None:
                        root = tk.Tk()
                        root.withdraw()
                    else:
                        root = tk._default_root
                    dialogo = TripleOptionDialog(root, mensaje_conflicto)
                    opcion = dialogo.result  # "atras", "actualizar" o "continuar"
                    if opcion == "atras" or opcion is None:
                        cursor.close()
                        conexion.close()
                        return False
                    elif opcion == "actualizar":
                        # Actualizar TODOS los registros para ese producto, lote y fechaIngreso = CURDATE
                        sql_actualiza_lote = """
                            UPDATE lotes_productos
                            SET vencimiento = %s,
                                cantidad_ingresada = cantidad_ingresada + %s,
                                cantidad_disponible = cantidad_disponible + %s
                            WHERE prodId = %s AND numeroLote = %s AND fechaIngreso = CURDATE()
                        """
                        cursor.execute(sql_actualiza_lote, (nuevo_vencimiento_str, cantidad, cantidad, prodId, lote_valor))
                    elif opcion == "continuar":
                        # En lugar de insertar una nueva fila (que genera duplicado), actualizamos la existente.
                        sql_actualiza_lote = """
                            UPDATE lotes_productos
                            SET cantidad_ingresada = cantidad_ingresada + %s,
                                cantidad_disponible = cantidad_disponible + %s
                            WHERE prodId = %s AND numeroLote = %s AND fechaIngreso = CURDATE()
                        """
                        cursor.execute(sql_actualiza_lote, (cantidad, cantidad, prodId, lote_valor))
                else:
                    # Si las fechas son iguales, se actualiza automáticamente sin diálogo.
                    sql_actualiza_lote = """
                        UPDATE lotes_productos
                        SET cantidad_ingresada = cantidad_ingresada + %s,
                            cantidad_disponible = cantidad_disponible + %s
                        WHERE prodId = %s AND numeroLote = %s AND fechaIngreso = CURDATE()
                    """
                    cursor.execute(sql_actualiza_lote, (cantidad, cantidad, prodId, lote_valor))
            else:
                # No existe registro para ese lote con fechaIngreso = CURDATE; se inserta uno nuevo.
                sql_insert_lote = """
                    INSERT INTO lotes_productos
                        (prodId, numeroLote, fechaIngreso, vencimiento, cantidad_ingresada, cantidad_disponible)
                    VALUES (%s, %s, CURDATE(), %s, %s, %s)
                """
                cursor.execute(sql_insert_lote, (prodId, lote_valor, nuevo_vencimiento_str, cantidad, cantidad))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True

        except Error as e:
            messagebox.showerror("Error en agregar/actualizar_producto:", e)
            return False

    def obtener_productos(self) -> list:
        """
        Retorna una lista de productos de la tabla "productos", considerando el stock total.
        Solo se retornan los productos activos.
        """
        productos = []
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("USE ventas_db")
                # Solo se retornan productos activos (activo = 1)
                cursor.execute("SELECT prodId, nombre, precio, stock FROM productos WHERE activo = 1")
                productos = cursor.fetchall()
                cursor.close()
                conexion.close()
        except Error as e:
            messagebox.showerror("Error al obtener productos:", e)
        return productos

# Parte actualizada en src/logica/gestor_stock.py

    def modificar_producto(self, parent, id_producto, producto_actualizado) -> bool:
        """
        Modifica los datos generales de un producto en la tabla 'productos'.
        En esta versión solo se actualizan los campos 'nombre' y 'precio', ya que el stock
        se calcula al vuelo a partir de los registros en lotes_productos y cualquier modificación
        de la información del lote (número de lote, cantidad disponible, vencimiento) se gestiona
        en la ventana detalle de lotes.
        
        Se valida que los campos 'nombre' y 'precio' estén completos, ya que son imprescindibles.
        """
        # Verificar que 'nombre' y 'precio' no estén vacíos
        if not producto_actualizado.get("nombre") or producto_actualizado.get("precio") is None:
            messagebox.showerror("Error", "Los campos 'nombre' y 'precio' son obligatorios.", parent=parent)
            return False
        
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return False
            cursor = conexion.cursor()
            cursor.execute("USE ventas_db")
            sql = "UPDATE productos SET nombre=%s, precio=%s WHERE prodId=%s"
            datos = (
                producto_actualizado["nombre"],
                producto_actualizado["precio"],
                id_producto
            )
            cursor.execute(sql, datos)
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
        except Error as e:
            messagebox.showerror("Error al modificar producto:", e, parent=parent)
            return False

    def eliminar_producto(self, id_producto) -> bool:
        """
        Realiza la eliminación lógica del producto:
        - Actualiza el campo "activo" a 0 en la tabla productos.
        - Actualiza todos los registros de lotes_productos asociados al producto
            poniendo 'cantidad_disponible' a 0.
        Retorna True si la operación es exitosa, False en caso de error.
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("USE ventas_db")
                # Eliminación lógica: actualizar activo a 0
                sql_producto = "UPDATE productos SET activo = 0, stock = 0 WHERE prodId = %s"
                cursor.execute(sql_producto, (id_producto,))

                # Actualizar los registros de lotes: poner cantidad_disponible en 0.
                sql_lotes = "UPDATE lotes_productos SET cantidad_disponible = 0 WHERE prodId = %s"
                cursor.execute(sql_lotes, (id_producto,))
                
                conexion.commit()
                cursor.close()
                conexion.close()
                return True
        except Error as e:
            messagebox.showerror("Error al eliminar producto:", e)
        return False


# Ejemplo de uso:
if __name__ == "__main__":
    stock_manager = StockManager()

    # Ejemplo: Agregar producto "Ibu" con el mismo lote pero con vencimientos distintos.
    producto1 = {
        "nombre": "Ibu",
        "precio": 1.5,
        "stock": 50,
        "lote": "Lote001",
        "vencimiento": "2025-04-17"
    }
    producto2 = {
        "nombre": "Ibu",
        "precio": 1.5,
        "stock": 30,
        "lote": "Lote001",
        "vencimiento": "2025-07-17"
    }
    print("Agregando producto 1:")
    if stock_manager.agregar_o_actualizar_producto(producto1):
        print("Producto 1 agregado/actualizado con éxito.")
    else:
        print("Error al agregar producto 1.")

    print("Agregando producto 2:")
    if stock_manager.agregar_o_actualizar_producto(producto2):
        print("Producto 2 agregado/actualizado con éxito.")
    else:
        print("Error al agregar producto 2.")

    productos = stock_manager.obtener_productos()
    print("Productos:", productos)
