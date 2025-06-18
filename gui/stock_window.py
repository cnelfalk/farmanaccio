# src/gui/stock_window.py
import customtkinter as ctk
from gui.login import icono_logotipo
from tkinter import ttk, messagebox, font as tkFont, simpledialog
from tkcalendar import DateEntry  
from utils.utilidades import Utilidades
from logica.gestor_vademecum import VademecumManager
from logica.gestor_stock import StockManager
from logica.gestor_inventario import GestorInventario  # Para inventario agrupado y detalles de lotes.
from gui.detalle_lotes import DetalleLotesWindow
import datetime

# --- Integración de la clase personalizada para DateEntry ---
class CustomDateEntry(DateEntry):
    def _drop_down(self):
        """
        Sobreescribe el método _drop_down para quitar el binding al evento <FocusOut>
        que hace que el calendario se cierre al navegar con las flechas.
        """
        top = super()._drop_down()
        top.unbind("<FocusOut>")
        return top
# --- Fin integración de CustomDateEntry ---

class StockWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Control de Stock")
        self.resizable(False, False)
        
        # Configurar dimensiones y centrar la ventana
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Instanciar gestores
        self.stock_manager = StockManager()
        self.vademecum_manager = VademecumManager()
        self.inventario_manager = GestorInventario()
        
        # Vincular evento para refrescar stock
        self.bind("<<DatosActualizados>>", self.refrescar_stock)
        
        # --- Sección de búsqueda ---
        self.frame_busqueda = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_busqueda.pack(fill="x", padx=10, pady=5)
        self.combo_busqueda = ctk.CTkComboBox(
            self.frame_busqueda,
            values=["Vademécum", "Stock", "Archivado"],  # Tres opciones
            width=120,
            command=lambda origen: self.cambiar_origen(origen)
        )
        self.combo_busqueda.set("Stock")
        self.combo_busqueda.pack(side="left", padx=5)
        self.entry_busqueda = ctk.CTkEntry(
            self.frame_busqueda,
            width=400,
            placeholder_text="Buscar producto..."
        )
        self.entry_busqueda.pack(side="left", padx=(0, 5))
        self.btn_busqueda = ctk.CTkButton(self.frame_busqueda, text="Buscar", command=self.buscar_productos)
        self.btn_busqueda.pack(side="left", padx=5)
        
        # --- Sección de tabla ---
        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.pack(fill="both", expand=True, padx=20, pady=(5, 10))
        self.tree = ttk.Treeview(self.frame_tabla, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.tag_configure("critical", background="#ffcccc", foreground="#660000")
        self.tree.tag_configure("warning", background="#ffffcc", foreground="#666600")
        self.tree.tag_configure("ok", background="#ccffcc", foreground="#006600")
        self.vscrollbar = ctk.CTkScrollbar(self.frame_tabla, orientation="vertical", command=self.tree.yview)
        self.vscrollbar.grid(row=0, column=1, sticky="ns")
        self.hscrollbar = ctk.CTkScrollbar(self.frame_tabla, orientation="horizontal", command=self.tree.xview)
        self.hscrollbar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.tree.configure(yscrollcommand=self.vscrollbar.set, xscrollcommand=self.hscrollbar.set)
        self.frame_tabla.rowconfigure(0, weight=1)
        self.frame_tabla.columnconfigure(0, weight=1)
        self.tree.bind("<Double-1>", self.mostrar_detalles)
        self.tree.bind("<<TreeviewSelect>>", self.cargar_datos_seleccionados)
        
        # --- Sección de formulario ---
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(fill="x", padx=100, pady=10)
        self.frame_form.grid_columnconfigure(0, weight=1)
        self.frame_form.grid_columnconfigure(1, weight=1)
        
        # Guardamos referencias a los campos "Nombre" y "Precio"
        self.label_nombre = ctk.CTkLabel(self.frame_form, text="Nombre:")
        self.label_nombre.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.entry_nombre = ctk.CTkEntry(self.frame_form, width=400)
        self.entry_nombre.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.label_precio = ctk.CTkLabel(self.frame_form, text="Precio:")
        self.label_precio.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_precio = ctk.CTkEntry(self.frame_form, width=400)
        self.entry_precio.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Continuación del formulario (campos propios de Stock y Vademécum)
        self.label_stock = ctk.CTkLabel(self.frame_form, text="Stock:")
        self.frame_stock = ctk.CTkFrame(self.frame_form)
        self.frame_stock.grid_columnconfigure(0, weight=0)
        self.frame_stock.grid_columnconfigure(1, weight=1)
        self.btn_decrementar = ctk.CTkButton(self.frame_stock, text="-", width=30, command=self.decrementar_stock)
        self.btn_decrementar.grid(row=0, column=0, padx=5)
        self.entry_stock = ctk.CTkEntry(self.frame_stock, width=250)
        self.entry_stock.grid(row=0, column=1, padx=5)
        self.btn_incrementar = ctk.CTkButton(self.frame_stock, text="+", width=30, command=self.incrementar_stock)
        self.btn_incrementar.grid(row=0, column=2, padx=5)
        
        self.label_lote = ctk.CTkLabel(self.frame_form, text="Lote:")
        self.entry_lote = ctk.CTkEntry(self.frame_form, width=400)
        
        self.label_vencimiento = ctk.CTkLabel(self.frame_form, text="Fecha de Vencimiento:")
        self.entry_vencimiento = CustomDateEntry(self.frame_form,
                                                 state="readonly",
                                                 locale="es_ES",
                                                 width=18,
                                                 date_pattern="yyyy-mm-dd",
                                                 background="lightblue",
                                                 foreground="black",
                                                 bordercolor="red")
        # Posicionamiento para Stock/Vademécum (inicialmente visibles)
        self.label_stock.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.frame_stock.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.label_lote.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.entry_lote.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.label_vencimiento.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.entry_vencimiento.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        # Contenedor de botones CRUD (fondo oscuro)
        self.frame_btns = ctk.CTkFrame(self.frame_form, fg_color="#2E2E2E")
        self.frame_btns.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        # Se configuran tres columnas para los botones; en Archivado usaremos columnspan para centrar.
        self.frame_btns.grid_columnconfigure(0, weight=1)
        self.frame_btns.grid_columnconfigure(1, weight=1)
        self.frame_btns.grid_columnconfigure(2, weight=1)
        # Creación de los botones CRUD
        self.btn_agregar = ctk.CTkButton(self.frame_btns, text="Agregar Producto", command=self.agregar)
        self.btn_agregar.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.btn_modificar = ctk.CTkButton(self.frame_btns, text="Modificar Producto", command=self.modificar)
        self.btn_modificar.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.btn_eliminar = ctk.CTkButton(self.frame_btns, text="Eliminar Producto", command=self.eliminar)
        self.btn_eliminar.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        # Botón de "Restaurar Producto" (inicialmente fuera de vista)
        self.btn_restaurar = ctk.CTkButton(self.frame_btns, text="Restaurar Producto", command=self.restaurar_producto)
        # Nota: No se asigna grid aquí porque se mostrará según el modo Archivado
        
        self.btn_volver = ctk.CTkButton(self, text="Volver", command=self.destroy)
        self.btn_volver.pack(padx=5, pady=(0, 8))
        
        self.cargar_datos_iniciales()
        self.after(150, lambda: self.iconbitmap(icono_logotipo))
    
    def refrescar_stock(self, event):
        self.cargar_productos()
    
    def cambiar_origen(self, origen):
        # Primero, ocultamos siempre el botón "Restaurar Producto"
        if hasattr(self, "btn_restaurar") and self.btn_restaurar is not None:
            self.btn_restaurar.grid_forget()
        
        if origen != "Archivado":
            # Configuración para los otros modos
            self.btn_agregar.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.btn_modificar.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.btn_eliminar.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
            self.label_nombre.grid()
            self.entry_nombre.grid()
            self.label_precio.grid()
            self.entry_precio.grid()
            # Restaurar el padding en el frame de botones si fuera necesario
            self.frame_btns.grid_configure(padx=0, pady=0)
        else:
            # En modo Archivado:
            self.btn_agregar.grid_forget()
            self.btn_modificar.grid_forget()
            self.btn_eliminar.grid_forget()
            self.label_nombre.grid_remove()
            self.entry_nombre.grid_remove()
            self.label_precio.grid_remove()
            self.entry_precio.grid_remove()

            # Configuramos el frame de botones para tener un padding extra
            self.frame_btns.grid_configure(padx=10, pady=10)
            # Hacemos que el frame se encoja en función de sus hijos:
            self.frame_btns.grid_propagate(True)
            
            # Posicionamos el botón "Restaurar Producto" sin forzar que se estire:
            self.btn_restaurar.grid_forget()  # Remover cualquier posicionamiento anterior
            self.btn_restaurar.grid(row=0, column=1, padx=10, pady=10)  # Sin sticky="ew"
        
        # Resto de la configuración de columnas, etc.
        if origen == "Stock":
            columns = ("ID", "Nombre", "Precio", "Stock", "Disponibilidad", "Vencimiento", "Detalle")
            self.btn_modificar.configure(state="normal")
            self.btn_eliminar.configure(state="normal")
            self.label_stock.grid_remove()
            self.frame_stock.grid_remove()
            self.label_lote.grid_remove()
            self.entry_lote.grid_remove()
            self.label_vencimiento.grid_remove()
            self.entry_vencimiento.grid_remove()
            self.cargar_productos()
        elif origen == "Vademécum":
            columns = ("Nombre Comercial", "Presentación", "Acción Farmacológica", "Principio Activo", "Laboratorio")
            self.btn_modificar.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")
            self.label_stock.grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.frame_stock.grid(row=2, column=1, padx=10, pady=5, sticky="w")
            self.label_lote.grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.entry_lote.grid(row=3, column=1, padx=10, pady=5, sticky="w")
            self.label_vencimiento.grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.entry_vencimiento.grid(row=4, column=1, padx=10, pady=5, sticky="w")
            self.cargar_vademecum()
        elif origen == "Archivado":
            columns = ("ID", "Nombre", "Precio", "Stock")
            self.btn_modificar.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")
            self.label_stock.grid_remove()
            self.frame_stock.grid_remove()
            self.label_lote.grid_remove()
            self.entry_lote.grid_remove()
            self.label_vencimiento.grid_remove()
            self.entry_vencimiento.grid_remove()
            self.cargar_productos_archivados()
        
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "ID":
                self.tree.column(col, width=50)
            elif col in ("Nombre", "Nombre Comercial"):
                self.tree.column(col, width=200)
            elif col in ("Precio", "Stock"):
                self.tree.column(col, width=100)
            elif col == "Disponibilidad":
                self.tree.column(col, width=120, anchor="center")
            elif col == "Acciones":
                self.tree.column(col, width=120, anchor="center")
            else:
                self.tree.column(col, width=150)

    
    def cargar_datos_iniciales(self):
        self.cambiar_origen(self.combo_busqueda.get())
    
    def buscar_productos(self):
        origen = self.combo_busqueda.get()
        termino = self.entry_busqueda.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        if origen == "Stock":
            inventario = self.inventario_manager.obtener_inventario_agrupado()
            if termino:
                inventario = [p for p in inventario if termino in p["nombre"].lower()]
            for p in inventario:
                venc = p.get("vencimiento_proximo") or ""
                estado = p.get("estado", self.inventario_manager._calcular_estado(p.get("total_stock", 0))[0])
                item = self.tree.insert("", "end", values=(
                    p["prodID"],
                    p["nombre"],
                    p["precio"],
                    p["total_stock"],
                    estado,
                    venc,
                    "Ver Detalle"
                ))
                if estado == "Crítico":
                    self.tree.item(item, tags=("critical",))
                elif estado == "Preocupante":
                    self.tree.item(item, tags=("warning",))
                else:
                    self.tree.item(item, tags=("ok",))
            self.ajustar_ancho_columnas()
        elif origen == "Vademécum":
            registros = self.vademecum_manager.buscar_vademecum(termino)
            for r in registros:
                self.tree.insert("", "end", values=(r["nombreComercial"],
                                                     r["presentacion"],
                                                     r["accionFarmacologica"],
                                                     r["principioActivo"],
                                                     r["laboratorio"]))
            self.ajustar_ancho_columnas()
        elif origen == "Archivado":
            self.cargar_productos_archivados()
    
    def cargar_productos(self):
        self.tree.delete(*self.tree.get_children())
        inventario = self.inventario_manager.obtener_inventario_agrupado()
        for p in inventario:
            venc = p.get("vencimiento_proximo") or ""
            estado = p.get("estado", self.inventario_manager._calcular_estado(p.get("total_stock", 0))[0])
            item = self.tree.insert("", "end", values=(
                p["prodID"],
                p["nombre"],
                p["precio"],
                p["total_stock"],
                estado,
                venc,
                "Ver Detalle"
            ))
            if estado == "Crítico":
                self.tree.item(item, tags=("critical",))
            elif estado == "Preocupante":
                self.tree.item(item, tags=("warning",))
            else:
                self.tree.item(item, tags=("ok",))
        self.ajustar_ancho_columnas()
    
    def cargar_vademecum(self):
        self.tree.delete(*self.tree.get_children())
        registros = self.vademecum_manager.obtener_vademecum()
        for r in registros:
            self.tree.insert("", "end", values=(r["nombreComercial"],
                                                 r["presentacion"],
                                                 r["accionFarmacologica"],
                                                 r["principioActivo"],
                                                 r["laboratorio"]))
        self.ajustar_ancho_columnas()
    
    def cargar_productos_archivados(self):
        self.tree.delete(*self.tree.get_children())
        productos = self.stock_manager.obtener_productos_archivados()
        for prod in productos:
            self.tree.insert("", "end", values=(
                prod["prodID"],
                prod["nombre"],
                prod["precio"],
                prod["stock"]
            ))
        self.ajustar_ancho_columnas()

    
    def ajustar_ancho_columnas(self):
        tree_font = tkFont.nametofont("TkDefaultFont")
        for col in self.tree["columns"]:
            max_width = tree_font.measure(col) + 10
            for item in self.tree.get_children():
                cell_text = str(self.tree.set(item, col))
                cell_width = tree_font.measure(cell_text) + 10
                if cell_width > max_width:
                    max_width = cell_width
            self.tree.column(col, width=max_width)
    
    def mostrar_detalles(self, event):
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if item and col == "#7":  # Columna "Detalle"
            values = self.tree.item(item, "values")
            prodID = values[0]
            self.abrir_detalles_producto(prodID, values)
    
    def abrir_detalles_producto(self, prodID, valores):
        detalles_generales = self.inventario_manager.obtener_detalles_generales_producto(valores[1])
        producto = {
            "prodID": prodID,
            "nombre": valores[1],
            "presentacion": detalles_generales.get("presentacion", "No Disponible"),
            "accionFarmacologica": detalles_generales.get("accionFarmacologica", "No Disponible"),
            "principioActivo": detalles_generales.get("principioActivo", "No Disponible"),
            "laboratorio": detalles_generales.get("laboratorio", "No Disponible")
        }
        detalles = self.inventario_manager.obtener_detalle_lotes(prodID)
        if not detalles:
            messagebox.showinfo("Detalle", "No se encontraron detalles de lotes para este producto.", parent=self)
            return
        from gui.detalle_lotes import DetalleLotesWindow
        DetalleLotesWindow(self, producto, detalles)
    
    def cargar_datos_seleccionados(self, _):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            if self.combo_busqueda.get() == "Stock":
                self.entry_nombre.delete(0, "end")
                self.entry_nombre.insert(0, values[1])
                self.entry_precio.delete(0, "end")
                self.entry_precio.insert(0, values[2])
            else:
                self.entry_nombre.delete(0, "end")
                self.entry_nombre.insert(0, values[0])
                self.entry_precio.delete(0, "end")
                self.entry_stock.delete(0, "end")
                self.entry_lote.delete(0, "end")
                self.entry_vencimiento.delete(0, "end")
    
    def incrementar_stock(self):
        try:
            current_stock = int(self.entry_stock.get())
        except ValueError:
            current_stock = 0
        new_stock = current_stock + 1
        self.entry_stock.delete(0, "end")
        self.entry_stock.insert(0, new_stock)
    
    def decrementar_stock(self):
        try:
            current_stock = int(self.entry_stock.get())
        except ValueError:
            current_stock = 0
        new_stock = current_stock - 1 if current_stock > 0 else 0
        self.entry_stock.delete(0, "end")
        self.entry_stock.insert(0, new_stock)
    
    def agregar(self):
        nombre = self.entry_nombre.get().strip()
        precio_text = self.entry_precio.get().strip()
        stock_text = self.entry_stock.get().strip()
        lote = self.entry_lote.get().strip()
        vencimiento = self.entry_vencimiento.get_date().isoformat()
        if not nombre or not precio_text or not stock_text or not vencimiento:
            messagebox.showwarning("Campos Vacíos", "Por favor, complete los campos obligatorios.")
            return
        try:
            precio = float(precio_text)
            stock = int(stock_text)
        except ValueError:
            messagebox.showerror("Error de Datos", "El precio y el stock deben ser numéricos.")
            return
        producto = {
            "nombre": nombre,
            "precio": precio,
            "stock": stock,
            "lote": lote,
            "vencimiento": vencimiento
        }
        if self.stock_manager.agregar_o_actualizar_producto(producto):
            messagebox.showinfo("Éxito", "Producto agregado/actualizado correctamente.")
            self.combo_busqueda.set("Stock")
            self.cambiar_origen("Stock")
            self.cargar_productos()
            self.entry_nombre.delete(0, "end")
            self.entry_precio.delete(0, "end")
            self.entry_stock.delete(0, "end")
            self.entry_lote.delete(0, "end")
        else:
            messagebox.showerror("Error", "No se pudo agregar/actualizar el producto.")
    
    def modificar(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Por favor, seleccione un producto para modificar.")
            return
        product_id = self.tree.item(selected, "values")[0]
        nombre = self.entry_nombre.get().strip()
        precio_text = self.entry_precio.get().strip()
        if not nombre or not precio_text:
            messagebox.showwarning("Campos Vacíos", "Ingrese nombre y precio para modificar.")
            return
        try:
            precio = float(precio_text)
        except ValueError:
            messagebox.showerror("Error de Datos", "El precio debe ser numérico.")
            return
        if self.stock_manager.modificar_producto(self, product_id, {"nombre": nombre, "precio": precio}):
            messagebox.showinfo("Éxito", "Producto modificado correctamente.")
            self.cargar_productos()
        else:
            messagebox.showerror("Error", "No se pudo modificar el producto.")
    
    def eliminar(self):
        sel = self.tree.focus()
        if not sel:
            return messagebox.showerror("Error","Seleccione un producto.",parent=self)
        prod_id = self.tree.item(sel, "values")[0]

        # Reutilizamos simpledialog de clientes
        razon = simpledialog.askstring(
            "Razón de archivado",
            "Indique el motivo para archivar este producto:",
            parent=self
        )
        if razon is None:
            return

        if self.stock_manager.eliminar_producto(prod_id, razon.strip()):
            messagebox.showinfo("Éxito","Producto archivado.", parent=self)
            self.cambiar_origen(self.combo_busqueda.get())
        else:
            messagebox.showerror("Error","No se pudo archivar el producto.", parent=self)
    
    def restaurar_producto(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Atención", "Seleccione un producto para restaurar.", parent=self)
            return
        valores = self.tree.item(selected_item, "values")
        prod_id = valores[0]
        if not messagebox.askyesno("Confirmar", "¿Desea restaurar este producto?"):
            return
        try:
            from datos.conexion_bd import ConexionBD
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            cursor.execute("UPDATE productos SET activo = 1 WHERE prodID = %s", (prod_id,))
            conexion.commit()
            cursor.close()
            conexion.close()
            messagebox.showinfo("Éxito", "Producto restaurado correctamente.")
            self.cargar_productos_archivados()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
    
if __name__ == "__main__":
    app = StockWindow()
    app.mainloop()
