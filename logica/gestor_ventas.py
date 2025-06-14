# src/logica/gestor_ventas.py

import customtkinter as ctk
from datos.conexion_bd import ConexionBD
from mysql.connector import Error
import tkinter.messagebox as messagebox
from datetime import datetime
import config  # Para manual_lote_selection
from logica.generar_factura import FacturaGenerator
from gui.login import icono_logotipo

class LoteSelectionDialog(ctk.CTkToplevel):
    """
    Diálogo modal para que el usuario seleccione manualmente un lote.
    """
    def __init__(self, parent, producto_id, lotes_list):
        super().__init__(parent)
        self.title("Selección de Lote")
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        # Texto indicativo
        label = ctk.CTkLabel(
            self,
            text=f"Para el producto ID {producto_id}, seleccione el lote a usar:",
            wraplength=400
        )
        label.pack(padx=20, pady=10)

        # Opciones formateadas
        opciones = [
            f"{l['numeroLote']} (Disp: {l['cantidad_disponible']})"
            for l in lotes_list
        ]
        self.combo = ctk.CTkComboBox(self, values=opciones, width=250)
        self.combo.pack(padx=20, pady=5)

        # Botón Aceptar
        btn = ctk.CTkButton(self, text="Aceptar", command=self.on_accept)
        btn.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(201, lambda: self.iconbitmap(icono_logotipo))
        self.wait_window()

    def on_accept(self):
        sel = self.combo.get()
        try:
            self.result = self.combo.values.index(sel)
        except ValueError:
            self.result = None
        self.destroy()

    def on_close(self):
        self.result = None
        self.destroy()


class VentaManager:
    """
    Gestor de ventas. Confirma la venta dentro de una transacción,
    aplica descuentos y genera la factura con datos de cliente.
    """
    def confirmar_venta(self, carrito, descuento=0.0, cliente=None, parent=None):
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return False, "No se pudo conectar a la base de datos."

            conexion.autocommit = False
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE farmanaccio_db")

            total_bruto = 0.0

            # 1) Procesar cada ítem: verificar stock y descontar lotes
            for item in carrito:
                prod_id = item["prodID"]
                qty = item["cantidad"]

                # Verificar stock global
                cursor.execute(
                    "SELECT stock, precio FROM productos WHERE prodID=%s",
                    (prod_id,)
                )
                fila = cursor.fetchone()
                if not fila or fila["stock"] < qty:
                    conexion.rollback()
                    return False, f"Stock insuficiente para producto ID {prod_id}."
                total_bruto += float(fila["precio"]) * qty

                # Obtener lotes ordenados por vencimiento
                cursor.execute("""
                    SELECT loteID, cantidad_disponible, numeroLote
                    FROM lotes_productos
                    WHERE prodID=%s AND cantidad_disponible>0
                    ORDER BY vencimiento ASC
                """, (prod_id,))
                lotes = cursor.fetchall()
                disponible = sum(l["cantidad_disponible"] for l in lotes)
                if disponible < qty:
                    conexion.rollback()
                    return False, f"No hay suficiente stock en lotes para ID {prod_id}."

                # Descontar por estrategia
                restante = qty
                if config.manual_lote_selection:
                    dialogo = LoteSelectionDialog(parent, prod_id, lotes)
                    idx = dialogo.result
                    if idx is None:
                        conexion.rollback()
                        return False, "Venta cancelada por el usuario."
                    lote = lotes[idx]
                    if lote["cantidad_disponible"] < restante:
                        conexion.rollback()
                        messagebox.showerror(
                            "Error",
                            f"Lote {lote['numeroLote']} no suficiente.",
                            parent=parent
                        )
                        return False, ""
                    nuevo_disp = lote["cantidad_disponible"] - restante
                    cursor.execute("""
                        UPDATE lotes_productos
                        SET cantidad_disponible=%s
                        WHERE loteID=%s
                    """, (nuevo_disp, lote["loteID"]))
                else:
                    for lote in lotes:
                        disp = lote["cantidad_disponible"]
                        if disp >= restante:
                            cursor.execute("""
                                UPDATE lotes_productos
                                SET cantidad_disponible=%s
                                WHERE loteID=%s
                            """, (disp-restante, lote["loteID"]))
                            restante = 0
                            break
                        else:
                            cursor.execute("""
                                UPDATE lotes_productos
                                SET cantidad_disponible=0
                                WHERE loteID=%s
                            """, (lote["loteID"],))
                            restante -= disp
                    if restante > 0:
                        conexion.rollback()
                        return False, f"No se pudo descontar stock suficiente para ID {prod_id}."

                # Actualizar stock global
                cursor.execute("""
                    UPDATE productos
                    SET stock = (
                        SELECT IFNULL(SUM(cantidad_disponible),0)
                        FROM lotes_productos
                        WHERE prodID=%s
                    )
                    WHERE prodID=%s
                """, (prod_id, prod_id))

            # 2) Calcular totales con descuento real
            dcto = float(descuento)
            total_neto = total_bruto * (1 - dcto/100)

            # 3) Insertar factura con descuento
            cursor.execute("""
                INSERT INTO facturas
                  (fechaEmision, horaEmision, total_neto, total_bruto, descuento)
                VALUES(CURRENT_DATE, CURRENT_TIME, %s, %s, %s)
            """, (total_neto, total_bruto, dcto))
            factura_id = cursor.lastrowid

            # 4) Insertar detalle de factura
            for item in carrito:
                pid = item["prodID"]
                qty = item["cantidad"]
                cursor.execute(
                    "SELECT precio FROM productos WHERE prodID=%s",
                    (pid,)
                )
                precio_unit = cursor.fetchone()["precio"]
                cursor.execute("""
                    INSERT INTO factura_detalles
                      (facturaID, prodID, cantidad, precioUnitario)
                    VALUES (%s,%s,%s,%s)
                """, (factura_id, pid, qty, precio_unit))

            # 5) Generar documento .docx/.pdf con cliente y descuento
            fg = FacturaGenerator()
            ok = fg.generar_factura_con_transaccion(
                parent, conexion, factura_id, cliente=cliente
            )
            if not ok:
                conexion.rollback()
                return False, "Generación de factura cancelada; venta no registrada."

            # 6) Commit final
            conexion.commit()
            return True, "Venta confirmada y factura generada exitosamente."

        except Error as e:
            if conexion:
                conexion.rollback()
            return False, str(e)
        finally:
            try: cursor.close()
            except: pass
            try: conexion.close()
            except: pass
