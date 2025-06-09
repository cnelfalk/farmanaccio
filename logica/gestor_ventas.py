# src/logica/gestor_ventas.py

import customtkinter as ctk
from datos.conexion_bd import ConexionBD
from mysql.connector import Error
import tkinter.messagebox as messagebox
from datetime import datetime
import config  # Para leer config.manual_lote_selection
from logica.generar_factura import FacturaGenerator

class LoteSelectionDialog(ctk.CTkToplevel):
    """
    Diálogo modal para que el usuario seleccione manualmente un lote.
    Se muestran en un combobox las opciones formateadas como:
      "NumeroLote (Disponible: X)"
    """
    def __init__(self, parent, producto_id, lotes_list):
        super().__init__(parent)
        self.title("Selección de Lote")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        self.options_list = lotes_list

        label_text = f"Para el producto ID {producto_id}, seleccione el lote a usar:"
        self.label = ctk.CTkLabel(self, text=label_text, wraplength=400)
        self.label.pack(padx=20, pady=10)

        opciones = [f"{l['numeroLote']} (Disponible: {l['cantidad_disponible']})" for l in lotes_list]
        self.combo = ctk.CTkComboBox(self, values=opciones, width=250)
        self.combo.pack(padx=20, pady=5)

        self.btn_ok = ctk.CTkButton(self, text="Aceptar", command=self.on_accept)
        self.btn_ok.pack(padx=20, pady=10)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.wait_window(self)

    def on_accept(self):
        selected_value = self.combo.get()
        opciones = [f"{l['numeroLote']} (Disponible: {l['cantidad_disponible']})" for l in self.options_list]
        try:
            idx = opciones.index(selected_value)
        except ValueError:
            idx = None
        self.result = idx
        self.destroy()

    def on_close(self):
        self.result = None
        self.destroy()

        
class VentaManager:
    """
    Clase que gestiona la confirmación de ventas. Todo el proceso se realiza
    dentro de una transacción que se confirma únicamente si la factura se genera y
    guarda correctamente. Si el usuario cancela la generación del archivo, se hace rollback.
    """
    def confirmar_venta(self, carrito, parent=None):
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return False, "No se pudo conectar a la base de datos."

            # Iniciar la transacción
            conexion.autocommit = False
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE farmanaccio_db")

            total_bruto = 0.0
            detalles_lote = {}  # (opcional)

            # Procesar cada producto del carrito
            for item in carrito:
                id_producto = item['prodId']
                cantidad_vendida = item['cantidad']

                # Consultar stock y precio
                cursor.execute("SELECT stock, precio FROM productos WHERE prodId=%s", (id_producto,))
                resultado = cursor.fetchone()
                if resultado is None:
                    conexion.rollback()
                    return False, f"Producto con ID {id_producto} no encontrado."
                stock_actual = resultado['stock']
                precio_unitario = resultado['precio']
                if stock_actual < cantidad_vendida:
                    conexion.rollback()
                    return False, f"Stock insuficiente para el producto ID {id_producto}."
                total_bruto += float(precio_unitario) * cantidad_vendida

                # Consultar lotes disponibles ordenados por fecha de vencimiento
                cursor.execute("""
                    SELECT loteID, numeroLote, cantidad_disponible, vencimiento 
                    FROM lotes_productos 
                    WHERE prodId=%s AND cantidad_disponible > 0 
                    ORDER BY vencimiento ASC
                """, (id_producto,))
                lotes = cursor.fetchall()
                total_disponible = sum(lote["cantidad_disponible"] for lote in lotes)
                if total_disponible < cantidad_vendida:
                    conexion.rollback()
                    return False, f"No hay suficiente stock en los lotes para el producto ID {id_producto}."

                if config.manual_lote_selection:
                    # Selección manual
                    dialogo = LoteSelectionDialog(parent, id_producto, lotes)
                    opcion = dialogo.result
                    if opcion is None:
                        conexion.rollback()
                        return False, "Venta cancelada por el usuario."
                    lote_seleccionado = lotes[opcion]
                    if cantidad_vendida > lote_seleccionado["cantidad_disponible"]:
                        conexion.rollback()
                        messagebox.showerror(
                            "Error",
                            f"La cantidad solicitada ({cantidad_vendida}) supera la disponibilidad del lote seleccionado ({lote_seleccionado['cantidad_disponible']}).",
                            parent=parent
                        )
                        return False, f"El lote {lote_seleccionado['numeroLote']} no tiene suficientes unidades."
                    # Actualizar solo el lote seleccionado
                    nuevo_stock = lote_seleccionado["cantidad_disponible"] - cantidad_vendida
                    cursor.execute("""
                        UPDATE lotes_productos
                        SET cantidad_disponible=%s
                        WHERE loteID=%s
                    """, (nuevo_stock, lote_seleccionado["loteID"]))
                else:
                    # Deducción automática
                    cantidad_restante = cantidad_vendida
                    for lote in lotes:
                        disponible = lote["cantidad_disponible"]
                        if disponible >= cantidad_restante:
                            nuevo_stock = disponible - cantidad_restante
                            cursor.execute("""
                                UPDATE lotes_productos
                                SET cantidad_disponible=%s
                                WHERE loteID=%s
                            """, (nuevo_stock, lote["loteID"]))
                            if id_producto not in detalles_lote:
                                detalles_lote[id_producto] = []
                            detalles_lote[id_producto].append({
                                "loteID": lote["loteID"],
                                "descontado": cantidad_restante,
                                "numeroLote": lote["numeroLote"]
                            })
                            cantidad_restante = 0
                            break
                        else:
                            cursor.execute("""
                                UPDATE lotes_productos
                                SET cantidad_disponible=0
                                WHERE loteID=%s
                            """, (lote["loteID"],))
                            if id_producto not in detalles_lote:
                                detalles_lote[id_producto] = []
                            detalles_lote[id_producto].append({
                                "loteID": lote["loteID"],
                                "descontado": disponible,
                                "numeroLote": lote["numeroLote"]
                            })
                            cantidad_restante -= disponible
                    if cantidad_restante > 0:
                        conexion.rollback()
                        return False, f"No se pudo descontar la cantidad requerida para el producto ID {id_producto}."

                # Actualizar stock global del producto
                cursor.execute("""
                    UPDATE productos
                    SET stock = (SELECT IFNULL(SUM(cantidad_disponible), 0) FROM lotes_productos WHERE prodId=%s)
                    WHERE prodId=%s
                """, (id_producto, id_producto))

            descuento = 0.0  
            total_neto = total_bruto * (1 - descuento / 100)

            # Insertar factura (sin commit)
            cursor.execute(
                """
                INSERT INTO facturas (fechaEmision, horaEmision, total_neto, total_bruto, descuento)
                VALUES (CURRENT_DATE, CURRENT_TIME, %s, %s, %s)
                """,
                (total_neto, total_bruto, descuento)
            )
            factura_id = cursor.lastrowid

            # Insertar detalle de factura (una línea por producto)
            for item in carrito:
                producto_id = item['prodId']
                cantidad_vendida = item['cantidad']
                cursor.execute("SELECT precio FROM productos WHERE prodId=%s", (producto_id,))
                precio_unitario = cursor.fetchone()['precio']
                cursor.execute(
                    """
                    INSERT INTO factura_detalles (facturaId, prodId, cantidad, precioUnitario)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (factura_id, producto_id, cantidad_vendida, precio_unitario)
                )

            # Generar la factura usando la conexión transaccional
            factura_generator = FacturaGenerator()
            exito_factura = factura_generator.generar_factura_con_transaccion(parent, conexion, factura_id)
            if not exito_factura:
                conexion.rollback()
                return False, "La generación de la factura fue cancelada; la venta no se registró."

            # Commit si todo sale bien
            conexion.commit()
            return True, "Venta confirmada y factura generada exitosamente."

        except Error as e:
            if conexion:
                conexion.rollback()
            return False, str(e)
        finally:
            try:
                cursor.close()
            except:
                pass
            try:
                conexion.close()
            except:
                pass

# Ejemplo de uso:
# vm = VentaManager()
# exito, mensaje = vm.confirmar_venta(carrito, parent)
# messagebox.showinfo("Resultado", mensaje, parent=parent)
