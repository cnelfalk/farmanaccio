# src/gui/detalle_lotes.py

import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry  
from datos.conexion_bd import ConexionBD
from gui.login import icono_logotipo
from mysql.connector import Error
import datetime

# Se modifica esta clase para que reciba, además, un diccionario "producto"
# que contenga (al menos) el prodId.
class DetalleLoteDetalleWindow(ctk.CTkToplevel):
    def __init__(self, master, lote_records, numero_lote, producto):
        super().__init__(master)
        self.title(f"Detalles para el Lote: {numero_lote}")
        self.lote_records = lote_records
        self.selected_record_id = None

        # Dimensiones de la ventana principal
        window_width = 600
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Almacenar la información del producto para actualizar luego el campo stock
        self.producto = producto  # Debe contener, por ejemplo, self.producto["prodId"]

        self.grab_set()

        label_title = ctk.CTkLabel(
            self, text=f"Registros para el Lote: {numero_lote}",
            font=("Arial", 14, "bold")
        )
        label_title.pack(pady=10)

        self.tree = ttk.Treeview(
            self, columns=("Fecha Ingreso", "Cantidad Ingresada", "Cantidad Disponible", "Vencimiento"),
            show="headings"
        )
        self.tree.heading("Fecha Ingreso", text="Fecha Ingreso")
        self.tree.heading("Cantidad Ingresada", text="Cantidad Ingresada")
        self.tree.heading("Cantidad Disponible", text="Cantidad Disponible")
        self.tree.heading("Vencimiento", text="Vencimiento")
        self.tree.column("Fecha Ingreso", width=100, anchor="center")
        self.tree.column("Cantidad Ingresada", width=120, anchor="center")
        self.tree.column("Cantidad Disponible", width=120, anchor="center")
        self.tree.column("Vencimiento", width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        for rec in lote_records:
            try:
                iid = rec["loteID"]
            except KeyError:
                messagebox.showerror("Error", "Uno de los registros no tiene 'loteID'.")
                continue
            fecha_ing = rec.get("fechaIngreso")
            if isinstance(fecha_ing, (datetime.date, datetime.datetime)):
                fecha_ing = fecha_ing.isoformat()
            venc = rec.get("vencimiento")
            if isinstance(venc, (datetime.date, datetime.datetime)):
                venc = venc.isoformat()
            self.tree.insert("", "end", iid=str(iid), values=(fecha_ing, rec.get("cantidad_ingresada"),
                                                              rec.get("cantidad_disponible"), venc))
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.mod_frame = ctk.CTkFrame(self)
        self.mod_frame.pack(fill="x", padx=10, pady=10)
        
        self.lbl_ingresada = ctk.CTkLabel(self.mod_frame, text="Cantidad Ingresada:")
        self.lbl_ingresada.grid(row=0, column=0, padx=5, pady=5)
        self.entry_ingresada = ctk.CTkEntry(self.mod_frame, width=80)
        self.entry_ingresada.grid(row=0, column=1, padx=5, pady=5)
        self.btn_inc_ing = ctk.CTkButton(self.mod_frame, text="+", command=self.incrementar_ingresada)
        self.btn_inc_ing.grid(row=0, column=2, padx=5, pady=5)
        self.btn_dec_ing = ctk.CTkButton(self.mod_frame, text="-", command=self.decrementar_ingresada)
        self.btn_dec_ing.grid(row=0, column=3, padx=5, pady=5)
        
        self.lbl_disponible = ctk.CTkLabel(self.mod_frame, text="Cantidad Disponible:")
        self.lbl_disponible.grid(row=1, column=0, padx=5, pady=5)
        self.entry_disponible = ctk.CTkEntry(self.mod_frame, width=80)
        self.entry_disponible.grid(row=1, column=1, padx=5, pady=5)
        self.btn_inc_disp = ctk.CTkButton(self.mod_frame, text="+", command=self.incrementar_disponible)
        self.btn_inc_disp.grid(row=1, column=2, padx=5, pady=5)
        self.btn_dec_disp = ctk.CTkButton(self.mod_frame, text="-", command=self.decrementar_disponible)
        self.btn_dec_disp.grid(row=1, column=3, padx=5, pady=5)

        self.lbl_vencimiento = ctk.CTkLabel(self.mod_frame, text="Fecha de Vencimiento:")
        self.lbl_vencimiento.grid(row=2, column=0, padx=5, pady=5)
        self.date_vencimiento = DateEntry(self.mod_frame, width=12, date_pattern="yyyy-mm-dd")
        self.date_vencimiento.grid(row=2, column=1, padx=5, pady=5)
        
        self.btn_confirm = ctk.CTkButton(
            self.mod_frame, text="Confirmar Modificación", command=self.confirmar_modificacion
        )
        self.btn_confirm.grid(row=3, column=0, columnspan=4, pady=10)
        
        ctk.CTkButton(self, text="Cerrar", command=self.destroy).pack(pady=5)

        self.after(201, lambda: self.iconbitmap(icono_logotipo))
    
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_record_id = selected[0]
            vals = self.tree.item(selected[0], "values")
            self.entry_ingresada.delete(0, "end")
            self.entry_ingresada.insert(0, vals[1])
            self.entry_disponible.delete(0, "end")
            self.entry_disponible.insert(0, vals[2])
            try:
                self.date_vencimiento.set_date(vals[3])
            except Exception:
                pass
                
    def incrementar_ingresada(self):
        try:
            actual = int(self.entry_ingresada.get())
        except:
            actual = 0
        self.entry_ingresada.delete(0, "end")
        self.entry_ingresada.insert(0, actual + 1)
    
    def decrementar_ingresada(self):
        try:
            actual = int(self.entry_ingresada.get())
        except:
            actual = 0
        if actual > 0:
            self.entry_ingresada.delete(0, "end")
            self.entry_ingresada.insert(0, actual - 1)
    
    def incrementar_disponible(self):
        try:
            actual = int(self.entry_disponible.get())
        except:
            actual = 0
        self.entry_disponible.delete(0, "end")
        self.entry_disponible.insert(0, actual + 1)
    
    def decrementar_disponible(self):
        try:
            actual = int(self.entry_disponible.get())
        except:
            actual = 0
        if actual > 0:
            self.entry_disponible.delete(0, "end")
            self.entry_disponible.insert(0, actual - 1)
    
    def confirmar_modificacion(self):
        if not self.selected_record_id:
            messagebox.showerror("Error", "No se ha seleccionado ningún registro para modificar.")
            return
        try:
            nueva_ingresada = int(self.entry_ingresada.get())
            nueva_disponible = int(self.entry_disponible.get())
        except ValueError:
            messagebox.showerror("Error", "Los valores deben ser numéricos.")
            return
        nuevo_vencimiento_str = self.date_vencimiento.get_date().isoformat()
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                messagebox.showerror("Error", "No se pudo establecer conexión.")
                return
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            sql = """
                UPDATE lotes_productos
                SET cantidad_ingresada = %s,
                    cantidad_disponible = %s,
                    vencimiento = %s
                WHERE loteID = %s
            """
            cursor.execute(sql, (nueva_ingresada, nueva_disponible, nuevo_vencimiento_str, self.selected_record_id))
            conexion.commit()
            
            # NUEVO: Actualizar también el campo "stock" en la tabla de productos
            sql_update_productos = """
                UPDATE productos
                SET stock = (
                    SELECT IFNULL(SUM(cantidad_disponible), 0)
                    FROM lotes_productos
                    WHERE prodId = %s
                )
                WHERE prodId = %s
            """
            cursor.execute(sql_update_productos, (self.producto["prodId"], self.producto["prodId"]))
            conexion.commit()
            
            cursor.close()
            conexion.close()
            messagebox.showinfo("Éxito", "Registro actualizado correctamente.", parent=self)
            current_vals = self.tree.item(self.selected_record_id, "values")
            self.tree.item(self.selected_record_id, values=(
                current_vals[0],
                nueva_ingresada,
                nueva_disponible,
                nuevo_vencimiento_str
            ))
            
            # Notificar a las ventanas superiores que se actualizaron los datos
            # Se usa el widget raíz para asegurar que el evento se propague globalmente.
            root = self.winfo_toplevel()
            root.event_generate("<<DatosActualizados>>", when="tail")
        except Error as e:
            messagebox.showerror("Error", f"No se pudo actualizar el registro:\n{e}", parent=self)


# Ahora se modifica la invocación en DetalleLotesWindow para pasar también la información del producto.
class DetalleLotesWindow(ctk.CTkToplevel):
    def __init__(self, master, producto, detalle_lotes):
        super().__init__(master)
        self.title(f"Detalle de Lotes: {producto.get('nombre')}")
        self.geometry("700x500")
        self.producto = producto  # Aquí se almacena toda la info del producto, incluido prodId
        self.detalle_lotes = detalle_lotes

        self.grab_set()

        # Dimensiones de la ventana principal
        window_width = 700
        window_height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        frame_general = ctk.CTkFrame(self)
        frame_general.pack(fill="x", padx=10, pady=10)
        
        info_producto = (
            f"Nombre: {producto.get('nombre')}\n"
            f"Presentación: {producto.get('presentacion', 'N/D')}\n"
            f"Acción Farmacológica: {producto.get('accionFarmacologica', 'N/D')}\n"
            f"Principio Activo: {producto.get('principioActivo', 'N/D')}\n"
            f"Laboratorio: {producto.get('laboratorio', 'N/D')}\n"
        )
        ctk.CTkLabel(frame_general, text=info_producto, justify="left", font=("Arial", 12)).pack(anchor="w")
        
        frame_tree = ctk.CTkFrame(self)
        frame_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(frame_tree, columns=("Lote", "Stock Disponible", "Vencimiento"), show="headings")
        self.tree.heading("Lote", text="Número de Lote")
        self.tree.heading("Stock Disponible", text="Stock Disponible")
        self.tree.heading("Vencimiento", text="Vencimiento")
        self.tree.column("Lote", width=150, anchor="center")
        self.tree.column("Stock Disponible", width=150, anchor="center")
        self.tree.column("Vencimiento", width=150, anchor="center")
        self.tree.pack(fill="both", expand=True)
        
        self.lotes_agrupados = {}
        for rec in detalle_lotes:
            numero = rec["numeroLote"]
            if numero in self.lotes_agrupados:
                self.lotes_agrupados[numero]["cantidad_disponible"] += rec["cantidad_disponible"]
                if rec["vencimiento"] < self.lotes_agrupados[numero]["vencimiento"]:
                    self.lotes_agrupados[numero]["vencimiento"] = rec["vencimiento"]
            else:
                self.lotes_agrupados[numero] = {
                    "cantidad_disponible": rec["cantidad_disponible"],
                    "vencimiento": rec["vencimiento"]
                }
        
        for lote, datos in self.lotes_agrupados.items():
            self.tree.insert("", "end", values=(lote, datos["cantidad_disponible"], datos["vencimiento"]))
        
        self.tree.bind("<Double-1>", self.ver_detalle_lote)
        
        ctk.CTkButton(self, text="Cerrar", command=self.destroy).pack(pady=10)

        self.after(201, lambda: self.iconbitmap(icono_logotipo))
    
    def ver_detalle_lote(self, event):
        item = self.tree.focus()
        if not item:
            return
        values = self.tree.item(item, "values")
        lote_seleccionado = values[0]
        registros_lote = [rec for rec in self.detalle_lotes if rec["numeroLote"] == lote_seleccionado]
        if not registros_lote:
            messagebox.showinfo("Detalle", "No hay registros para este lote.", parent=self)
            return
        # Se pasa self.producto a la ventana de detalle de lote
        from gui.detalle_lotes import DetalleLoteDetalleWindow
        DetalleLoteDetalleWindow(self, registros_lote, lote_seleccionado, self.producto)

# Ejemplo de uso (simulación):
if __name__ == "__main__":
    producto_ejemplo = {
        "prodId": 1,
        "nombre": "Aspirina",
        "presentacion": "Tabletas de 500 mg",
        "accionFarmacologica": "Analgésico/Antiinflamatorio",
        "principioActivo": "Ácido acetilsalicílico",
        "laboratorio": "FarmacoLab"
    }
    detalle_lotes_ejemplo = [
        {"loteID": 1, "numeroLote": "LoteA", "fechaIngreso": "2024-01-15", "vencimiento": "2025-06-30", "cantidad_ingresada": 50, "cantidad_disponible": 10},
        {"loteID": 2, "numeroLote": "LoteA", "fechaIngreso": "2024-02-10", "vencimiento": "2025-06-30", "cantidad_ingresada": 30, "cantidad_disponible": 30},
        {"loteID": 3, "numeroLote": "LoteB", "fechaIngreso": "2024-03-05", "vencimiento": "2025-04-15", "cantidad_ingresada": 100, "cantidad_disponible": 100},
    ]
    import customtkinter as ctk
    app = ctk.CTk()
    app.withdraw()
    ventana = DetalleLotesWindow(app, producto_ejemplo, detalle_lotes_ejemplo)
    ventana.mainloop()
