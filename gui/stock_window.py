# src/gui/stock_window.py
import customtkinter as ctk
from gui.login import icono_logotipo
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from utils.utilidades import Utilidades
from logica.gestor_vademecum import VademecumManager
from logica.gestor_stock import StockManager
from logica.gestor_inventario import GestorInventario  # Para inventario agrupado y detalles de lotes.
from gui.detalle_lotes import DetalleLotesWindow  # Ventana para ver detalle de lotes.

class StockWindow(ctk.CTkToplevel):
    """
    Ventana para el control de stock.
    
    Permite elegir entre dos modos:
      - "Stock": muestra el inventario agrupado a partir del GestorInventario, con las columnas:
          ID, Nombre, Precio, Stock, Vencimiento y Detalle.
        En esta vista se muestra el texto "Ver Detalle" en la columna "Detalle".
        Al hacer doble clic sobre esa columna se abre la ventana de detalle de lotes.
        
      - "Vademécum": muestra el catálogo importado. En este modo se desactivan los botones
        de "Modificar Producto" y "Eliminar Producto".
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Control de Stock")
        self.resizable(False, False)
        
        # Dimensiones y centrado
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Gestores
        self.stock_manager = StockManager()
        self.vademecum_manager = VademecumManager()
        self.inventario_manager = GestorInventario()
        
        # -------------------- Área de Búsqueda --------------------
        self.frame_busqueda = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_busqueda.pack(fill="x", padx=10, pady=5)
        self.combo_busqueda = ctk.CTkComboBox(self.frame_busqueda,
                                              values=["Stock", "Vademécum"],
                                              width=120,
                                              command=lambda origen: self.cambiar_origen(origen))
        self.combo_busqueda.set("Stock")
        self.combo_busqueda.pack(side="left", padx=5)
        self.entry_busqueda = ctk.CTkEntry(self.frame_busqueda,
                                          width=400,
                                          placeholder_text="Buscar producto...")
        self.entry_busqueda.pack(side="left", padx=(0, 5))
        self.btn_busqueda = ctk.CTkButton(self.frame_busqueda, text="Buscar", command=self.buscar_productos)
        self.btn_busqueda.pack(side="left", padx=5)
        
        # -------------------- Área del TreeView (usando grid y show="headings") --------------------
        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.pack(fill="both", expand=True, padx=20, pady=(5, 10))
        
        self.tree = ttk.Treeview(self.frame_tabla, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        self.vscrollbar = ctk.CTkScrollbar(self.frame_tabla, orientation="vertical", command=self.tree.yview)
        self.vscrollbar.grid(row=0, column=1, sticky="ns")
        
        self.hscrollbar = ctk.CTkScrollbar(self.frame_tabla, orientation="horizontal", command=self.tree.xview)
        self.hscrollbar.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.tree.configure(yscrollcommand=self.vscrollbar.set, xscrollcommand=self.hscrollbar.set)
        self.frame_tabla.rowconfigure(0, weight=1)
        self.frame_tabla.columnconfigure(0, weight=1)
        
        self.tree.bind("<Double-1>", self.mostrar_detalles)
        self.tree.bind("<<TreeviewSelect>>", self.cargar_datos_seleccionados)
        
        # -------------------- Formulario de Edición --------------------
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(fill="x", padx=100, pady=10)
        ctk.CTkLabel(self.frame_form, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_nombre = ctk.CTkEntry(self.frame_form, width=400)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(self.frame_form, text="Precio:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_precio = ctk.CTkEntry(self.frame_form, width=400)
        self.entry_precio.grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkLabel(self.frame_form, text="Stock:").grid(row=2, column=0, padx=10, pady=5)
        self.frame_stock = ctk.CTkFrame(self.frame_form)
        self.frame_stock.grid(row=2, column=1, padx=5, pady=5)
        self.btn_decrementar = ctk.CTkButton(self.frame_stock, text="-", width=30, command=self.decrementar_stock)
        self.btn_decrementar.pack(side="left")
        self.entry_stock = ctk.CTkEntry(self.frame_stock, width=250)
        self.entry_stock.pack(side="left")
        self.btn_incrementar = ctk.CTkButton(self.frame_stock, text="+", width=30, command=self.incrementar_stock)
        self.btn_incrementar.pack(side="left")
        ctk.CTkLabel(self.frame_form, text="Lote:").grid(row=3, column=0, padx=10, pady=5)
        self.entry_lote = ctk.CTkEntry(self.frame_form, width=400)
        self.entry_lote.grid(row=3, column=1, padx=5, pady=5)
        ctk.CTkLabel(self.frame_form, text="Fecha de Vencimiento:").grid(row=4, column=0, padx=10, pady=5)
        self.entry_vencimiento = DateEntry(self.frame_form, width=18, date_pattern='yyyy-mm-dd')
        self.entry_vencimiento.grid(row=4, column=1, padx=5, pady=5)
        
        # -------------------- Botones de Acción --------------------
        self.frame_btns = ctk.CTkFrame(self.frame_form, fg_color="#2E2E2E")
        self.frame_btns.grid(row=5, column=0, columnspan=2, pady=10)
        self.btn_agregar = ctk.CTkButton(self.frame_btns, text="Agregar Producto", command=self.agregar)
        self.btn_agregar.grid(row=0, column=0, padx=5, pady=5)
        self.btn_modificar = ctk.CTkButton(self.frame_btns, text="Modificar Producto", command=self.modificar)
        self.btn_modificar.grid(row=0, column=1, padx=5, pady=5)
        self.btn_eliminar = ctk.CTkButton(self.frame_btns, text="Eliminar Producto", command=self.eliminar)
        self.btn_eliminar.grid(row=0, column=2, padx=5, pady=5)
        self.btn_volver = ctk.CTkButton(self, text="Volver", command=self.destroy)
        self.btn_volver.pack(padx=5, pady=(0,8))
        
        # Cargar datos iniciales según la selección actual en el ComboBox.
        self.cargar_datos_iniciales()
        self.after(150, lambda: self.iconbitmap(icono_logotipo))
    
    def cambiar_origen(self, origen):
        """
        Configura el TreeView según el origen de los datos:
          - Si es "Stock", se muestran las columnas:
                ("ID", "Nombre", "Precio", "Stock", "Vencimiento", "Detalle")
          - Si es "Vademécum", se usan las columnas correspondientes al catálogo.
        Además, si se selecciona "Vademécum", se deshabilitan automáticamente 
        los botones "Modificar Producto" y "Eliminar Producto".
        """
        if origen == "Stock":
            columns = ("ID", "Nombre", "Precio", "Stock", "Vencimiento", "Detalle")
            self.btn_modificar.configure(state="normal")
            self.btn_eliminar.configure(state="normal")
        else:
            columns = ("nombre-comercial", "presentacion", "accion-farmacologica", "principios-activos", "laboratorio")
            self.btn_modificar.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "ID":
                self.tree.column(col, width=50)
            elif col in ("Nombre", "nombre-comercial"):
                self.tree.column(col, width=200)
            elif col in ("Precio", "Stock"):
                self.tree.column(col, width=100)
            else:
                self.tree.column(col, width=150)
        self.tree.delete(*self.tree.get_children())
        if self.combo_busqueda.get() == "Stock":
            self.cargar_productos()
        else:
            self.cargar_vademecum()
    
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
                self.tree.insert("", "end", values=(
                    p["prodId"],
                    p["nombre"],
                    p["precio"],
                    p["total_stock"],
                    venc,
                    "Ver Detalle"
                ))
        else:
            registros = self.vademecum_manager.buscar_vademecum(termino)
            for r in registros:
                self.tree.insert("", "end", values=(
                    r["nombreComercial"],
                    r["presentacion"],
                    r["accionFarmacologica"],
                    r["principioActivo"],
                    r["laboratorio"]
                ))
    
    def cargar_productos(self):
        self.tree.delete(*self.tree.get_children())
        inventario = self.inventario_manager.obtener_inventario_agrupado()
        for p in inventario:
            venc = p.get("vencimiento_proximo") or ""
            self.tree.insert("", "end", values=(
                p["prodId"],
                p["nombre"],
                p["precio"],
                p["total_stock"],
                venc,
                "Ver Detalle"
            ))
    
    def cargar_vademecum(self):
        self.tree.delete(*self.tree.get_children())
        registros = self.vademecum_manager.obtener_vademecum()
        for r in registros:
            self.tree.insert("", "end", values=(
                r["nombreComercial"],
                r["presentacion"],
                r["accionFarmacologica"],
                r["principioActivo"],
                r["laboratorio"]
            ))
    
    def agregar(self):
        try:
            producto = {
                "nombre": self.entry_nombre.get().strip(),
                "precio": float(self.entry_precio.get()),
                "stock": int(self.entry_stock.get())
            }
            producto["lote"] = self.entry_lote.get().strip()
            producto["vencimiento"] = self.entry_vencimiento.get()  # DateEntry ya devuelve la fecha formateada.
        except ValueError:
            messagebox.showerror("Error", "Precio y Stock deben ser numéricos.", parent=self)
            return
        if Utilidades.confirmar_accion(self, "agregar este producto", tipo_usuario="administrador"):
            if self.stock_manager.agregar_o_actualizar_producto(producto):
                messagebox.showinfo("Éxito", "Producto agregado/actualizado exitosamente!", parent=self)
                if self.combo_busqueda.get() == "Stock":
                    self.cargar_productos()
                else:
                    self.cargar_vademecum()
            else:
                messagebox.showerror("Error", "No se pudo agregar/actualizar el producto.", parent=self)
    
    def modificar(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un producto para modificar.", parent=self)
            return
        values = self.tree.item(selected_item, "values")
        id_producto = values[0]
        try:
            producto_actualizado = {
                "nombre": self.entry_nombre.get().strip(),
                "precio": float(self.entry_precio.get()),
                "stock": int(self.entry_stock.get())
            }
            producto_actualizado["lote"] = self.entry_lote.get().strip()
            producto_actualizado["vencimiento"] = self.entry_vencimiento.get()
        except ValueError:
            messagebox.showerror("Error", "Precio y Stock deben ser numéricos.", parent=self)
            return
        if Utilidades.confirmar_accion(self, "modificar este producto", tipo_usuario="administrador"):
            if self.stock_manager.modificar_producto(self, id_producto, producto_actualizado):
                messagebox.showinfo("Éxito", "Producto modificado exitosamente!", parent=self)
                if self.combo_busqueda.get() == "Stock":
                    self.cargar_productos()
                else:
                    self.cargar_vademecum()
            else:
                messagebox.showerror("Error", "Error al modificar producto.", parent=self)
    
    def eliminar(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un producto para eliminar.", parent=self)
            return
        values = self.tree.item(selected_item, "values")
        id_producto = values[0]
        if Utilidades.confirmar_accion(self, "eliminar este producto", tipo_usuario="administrador"):
            if self.stock_manager.eliminar_producto(id_producto):
                messagebox.showinfo("Éxito", "Producto eliminado exitosamente!", parent=self)
                if self.combo_busqueda.get() == "Stock":
                    self.cargar_productos()
                else:
                    self.cargar_vademecum()
            else:
                messagebox.showerror("Error", "Error al eliminar producto.", parent=self)
    
    def cargar_datos_seleccionados(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            if self.combo_busqueda.get() == "Stock":
                self.entry_nombre.delete(0, "end")
                self.entry_nombre.insert(0, values[1])
                self.entry_precio.delete(0, "end")
                self.entry_precio.insert(0, values[2])
                self.entry_stock.delete(0, "end")
                self.entry_stock.insert(0, values[3])
                # En la vista agrupada, no mostramos datos específicos de lote y vencimiento, se limpian.
                self.entry_lote.delete(0, "end")
                self.entry_vencimiento.delete(0, "end")
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
    
    def mostrar_detalles(self, event):
        """
        Detecta doble clic en la columna "Detalle" (la sexta columna en modo Stock)
        y abre la ventana de detalle de lotes para el producto seleccionado.
        """
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if item and col == "#6":
            values = self.tree.item(item, "values")
            prodId = values[0]
            self.abrir_detalles_producto(prodId, values)
    
    def abrir_detalles_producto(self, prodId, valores):
        """
        Obtiene la información general extendida del producto (incluyendo presentación,
        acción farmacológica, principio activo y laboratorio) mediante el GestorInventario,
        y abre la ventana de detalle de lotes.
        """
        detalles_generales = self.inventario_manager.obtener_detalles_generales_producto(valores[1])
        producto = {
            "prodId": prodId,
            "nombre": valores[1],
            "presentacion": detalles_generales.get("presentacion", "No Disponible"),
            "accionFarmacologica": detalles_generales.get("accionFarmacologica", "No Disponible"),
            "principioActivo": detalles_generales.get("principioActivo", "No Disponible"),
            "laboratorio": detalles_generales.get("laboratorio", "No Disponible")
        }
        detalles = self.inventario_manager.obtener_detalle_lotes(prodId)
        if not detalles:
            messagebox.showinfo("Detalle", "No se encontraron detalles de lotes para este producto.", parent=self)
            return
        DetalleLotesWindow(self, producto, detalles)

# Ejemplo de uso:
if __name__ == "__main__":
    app = StockWindow()
    app.mainloop()
