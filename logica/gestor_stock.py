# src/logica/gestor_stock.py
import tkinter.messagebox as messagebox
import datetime
import customtkinter as ctk  # Para el diálogo personalizado
from datos.conexion_bd import ConexionBD
from mysql.connector import Error
from utils.utilidades import Utilidades
from gui.login import icono_logotipo

# --- Nueva clase para preguntar por el precio ---
class PrecioOptionDialog(ctk.CTkToplevel):
    """
    Diálogo modal con tres opciones: "Atrás", "Actualizar" y "Mantener".
    Se usa cuando, para un producto ya existente, el precio ingresado es distinto
    al precio actual registrado en la base de datos.
    """
    def __init__(self, parent, nombre_producto, precio_actual, precio_nuevo):
        super().__init__(parent)
        self.title("Conflicto de Precio")
        self.result = None
        self.grab_set()
        self.resizable(False, False)
        self.geometry("400x200")

        mensaje = (
            f"El producto '{nombre_producto}' ya existe con precio {precio_actual}.\n"
            f"El nuevo precio ingresado es {precio_nuevo}.\n\n"
            "¿Desea actualizar el precio a la nueva cifra o mantener el precio vigente?"
        )
        ctk.CTkLabel(self, text=mensaje, wraplength=380, justify="center").pack(padx=10, pady=20)

        frame_buttons = ctk.CTkFrame(self)
        frame_buttons.pack(pady=10)

        btn_atras = ctk.CTkButton(frame_buttons, text="Atrás", command=lambda: self._cerrar("atras"))
        btn_atras.grid(row=0, column=0, padx=5)

        btn_actualizar = ctk.CTkButton(frame_buttons, text="Actualizar", command=lambda: self._cerrar("actualizar"))
        btn_actualizar.grid(row=0, column=1, padx=5)

        btn_mantener = ctk.CTkButton(frame_buttons, text="Mantener", command=lambda: self._cerrar("mantener"))
        btn_mantener.grid(row=0, column=2, padx=5)

        self.protocol("WM_DELETE_WINDOW", lambda: self._cerrar("atras"))
        self.wait_window()

    def _cerrar(self, resultado):
        self.result = resultado
        self.destroy()


class TripleOptionDialog(ctk.CTkToplevel):
    """
    Diálogo modal con tres opciones: "Atrás", "Actualizar" y "Continuar".
    Se usa cuando, para un producto con el mismo lote y la misma fecha de ingreso,
    el vencimiento ingresado es distinto al vencimiento ya registrado.
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

        self.after(201, lambda: self.iconbitmap(icono_logotipo))

        self.protocol("WM_DELETE_WINDOW", lambda: self._cerrar("atras"))
        self.wait_window()

    def _cerrar(self, resultado):
        self.result = resultado
        self.destroy()


class StockManager:
    """
    Clase que maneja la lógica para la gestión de productos y lotes.
    """
    def _calcular_indicador(self, stock: int) -> str:
        """
        Calcula el indicador basado en el stock:
         - Menos de 10 → retorna "Crítico"
         - Entre 10 y 29 → retorna "Preocupante"
         - 30 o más → retorna "Razonable"
        """
        if stock < 10:
            return "Crítico"
        elif stock < 30:
            return "Preocupante"
        else:
            return "Razonable"

    def agregar_o_actualizar_producto(self, producto) -> bool:
        """
        Agrega o actualiza un producto y registra el lote correspondiente.
        (No se agrega ningún campo en la BD para el indicador; se calcula en tiempo real).
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
            cursor.execute("USE farmanaccio_db")
            # Buscar si existe un producto (ignorando mayúsculas)
            sql_busqueda = "SELECT prodId, stock, activo, precio FROM productos WHERE LOWER(nombre) = LOWER(%s)"
            cursor.execute(sql_busqueda, (producto["nombre"],))
            resultado = cursor.fetchone()
            nuevo_stock = producto["stock"]
            if resultado:
                prodId = resultado["prodId"]
                if resultado["activo"] == 1:
                    stock_actual = resultado["stock"]
                    nuevo_stock = stock_actual + producto["stock"]

                    # Verificar conflicto de precio
                    new_price = producto["precio"]
                    if float(new_price) != float(resultado["precio"]):
                        # Prepara el diálogo para decidir qué hacer con el precio
                        from tkinter import Tk
                        try:
                            if Tk._default_root is None:
                                root = Tk()
                                root.withdraw()
                            else:
                                root = Tk._default_root
                        except Exception:
                            root = None
                        dialog = PrecioOptionDialog(root, producto["nombre"], resultado["precio"], new_price)
                        opcion = dialog.result
                        if opcion is None or opcion == "atras":
                            cursor.close()
                            conexion.close()
                            return False
                        elif opcion == "actualizar":
                            new_price = new_price  # se usará el precio nuevo
                        elif opcion == "mantener":
                            new_price = resultado["precio"]

                    sql_update = "UPDATE productos SET stock = %s, precio = %s WHERE prodId = %s"
                    cursor.execute(sql_update, (nuevo_stock, new_price, prodId))
                else:
                    confirmacion = messagebox.askyesno(
                        "Reactivar producto",
                        "Se encontró un registro inactivo para este producto. ¿Deseas reactivarlo y reiniciar el stock con el nuevo valor?",
                        parent=None
                    )
                    if confirmacion:
                        sql_reactivar = "UPDATE productos SET stock = %s, precio = %s, activo = 1 WHERE prodId = %s"
                        cursor.execute(sql_reactivar, (nuevo_stock, producto["precio"], prodId))
                    else:
                        sql_insert = "INSERT INTO productos (nombre, precio, stock, activo) VALUES (%s, %s, %s, 1)"
                        cursor.execute(sql_insert, (producto["nombre"], producto["precio"], nuevo_stock))
                        prodId = cursor.lastrowid
            else:
                sql_insert = "INSERT INTO productos (nombre, precio, stock, activo) VALUES (%s, %s, %s, 1)"
                cursor.execute(sql_insert, (producto["nombre"], producto["precio"], nuevo_stock))
                prodId = cursor.lastrowid

            # Procesar la tabla lotes_productos
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
                if nuevo_vencimiento is not None:
                    if isinstance(registro_lote["vencimiento"], (datetime.date, datetime.datetime)):
                        vencimiento_existente_str = registro_lote["vencimiento"].isoformat()
                    else:
                        vencimiento_existente_str = str(registro_lote["vencimiento"])
                    nuevo_vencimiento_str = str(nuevo_vencimiento)
                    if nuevo_vencimiento_str != vencimiento_existente_str:
                        mensaje_conflicto = (
                            f"El lote '{lote_valor}' ya existe con vencimiento {vencimiento_existente_str}.\n\n"
                            f"¿Deseas actualizar la fecha de vencimiento a la nueva ingresada ({nuevo_vencimiento_str}) "
                            "o continuar usando la fecha vigente?"
                        )
                        from tkinter import Tk
                        try:
                            if Tk._default_root is None:
                                root = Tk()
                                root.withdraw()
                            else:
                                root = Tk._default_root
                        except Exception:
                            root = None
                        dialogo = TripleOptionDialog(root, mensaje_conflicto)
                        opcion = dialogo.result
                        if opcion == "atras" or opcion is None:
                            cursor.close()
                            conexion.close()
                            return False
                        elif opcion == "actualizar":
                            cursor.execute("""
                                UPDATE lotes_productos
                                SET vencimiento = %s,
                                    cantidad_ingresada = cantidad_ingresada + %s,
                                    cantidad_disponible = cantidad_disponible + %s
                                WHERE prodId = %s AND numeroLote = %s AND fechaIngreso = CURDATE()
                            """, (nuevo_vencimiento_str, cantidad, cantidad, prodId, lote_valor))
                        elif opcion == "continuar":
                            cursor.execute("""
                                UPDATE lotes_productos
                                SET cantidad_ingresada = cantidad_ingresada + %s,
                                    cantidad_disponible = cantidad_disponible + %s
                                WHERE prodId = %s AND numeroLote = %s AND fechaIngreso = CURDATE()
                            """, (cantidad, cantidad, prodId, lote_valor))
                    else:
                        cursor.execute("""
                            UPDATE lotes_productos
                            SET cantidad_ingresada = cantidad_ingresada + %s,
                                cantidad_disponible = cantidad_disponible + %s
                            WHERE prodId = %s AND numeroLote = %s AND fechaIngreso = CURDATE()
                        """, (cantidad, cantidad, prodId, lote_valor))
                else:
                    # Si no hay vencimiento (aunque se valida antes) se actualiza solo la cantidad
                    cursor.execute("""
                        UPDATE lotes_productos
                        SET cantidad_ingresada = cantidad_ingresada + %s,
                            cantidad_disponible = cantidad_disponible + %s
                        WHERE prodId = %s AND numeroLote = %s AND fechaIngreso = CURDATE()
                    """, (cantidad, cantidad, prodId, lote_valor))
            else:
                nuevo_vencimiento_str = str(nuevo_vencimiento)
                cursor.execute("""
                    INSERT INTO lotes_productos
                        (prodId, numeroLote, fechaIngreso, vencimiento, cantidad_ingresada, cantidad_disponible)
                    VALUES (%s, %s, CURDATE(), %s, %s, %s)
                """, (prodId, lote_valor, nuevo_vencimiento_str, cantidad, cantidad))
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
        except Error as e:
            messagebox.showerror("Error en agregar/actualizar_producto:", e)
            return False

    def obtener_productos(self) -> list:
        """
        Retorna una lista de productos de la tabla "productos" consultando los campos existentes.
        Se añade de forma local el atributo "indicador", calculado a partir del stock.
        """
        productos = []
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("USE farmanaccio_db")
                cursor.execute("SELECT prodId, nombre, precio, stock FROM productos WHERE activo = 1")
                productos = cursor.fetchall()
                cursor.close()
                conexion.close()
                # Para cada producto, calcular el indicador (sin guardarlo en BD)
                for prod in productos:
                    prod["indicador"] = self._calcular_indicador(prod["stock"])
        except Error as e:
            messagebox.showerror("Error al obtener productos:", e)
        return productos

    def modificar_producto(self, parent, id_producto, producto_actualizado) -> bool:
        if not producto_actualizado.get("nombre") or producto_actualizado.get("precio") is None:
            messagebox.showerror("Error", "Los campos 'nombre' y 'precio' son obligatorios.", parent=parent)
            return False
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return False
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
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
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("USE farmanaccio_db")
                sql_producto = "UPDATE productos SET activo = 0, stock = 0 WHERE prodId = %s"
                cursor.execute(sql_producto, (id_producto,))
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

    producto1 = {
        "nombre": "Ibu",
        "precio": 1.5,
        "stock": 50,
        "lote": "Lote001",
        "vencimiento": "2025-04-17"
    }
    producto2 = {
        "nombre": "Ibu",
        "precio": 2.0,  # Precio distinto para probar el diálogo de conflicto
        "stock": 30,
        "lote": "Lote001",
        "vencimiento": "2025-04-17"
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
