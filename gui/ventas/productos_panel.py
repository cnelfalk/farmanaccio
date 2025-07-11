# src/gui/ventas/productos_panel.py
import customtkinter as ctk
from tkinter import ttk, font as tkFont

class PanelProductos(ctk.CTkFrame):
    def __init__(self, master, on_buscar, on_refrescar, on_seleccion, on_agregar, cantidad_var):
        super().__init__(master, fg_color="#408E57")

        self.on_seleccion = on_seleccion
        self.cantidad_var = cantidad_var

        ctk.CTkLabel(self, text="Productos Disponibles", font=("Arial", 16)).pack(padx=5, pady=5)

        # Área de búsqueda
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(padx=10, pady=5, expand=True)
        search_frame_inside = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_frame_inside.pack(padx=5)
        self.entry_search = ctk.CTkEntry(search_frame_inside, width=500, placeholder_text="Buscar producto...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(search_frame_inside, text="Buscar", command=on_buscar).pack()

        # Treeview de productos (incluyendo la columna "Disponibilidad")
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(padx=5, pady=5, fill="both", expand=True)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("ID", "Producto", "Precio Unit.", "Stock", "Disponibilidad"),
            show="headings"
        )
        # Define las cabeceras sin abreviaciones y con anchuras ajustadas (inicialmente)
        for col, ancho, anchor in zip(
            ["ID", "Producto", "Precio Unit.", "Stock", "Disponibilidad"],
            [50, 200, 100, 100, 120],
            ["center", "w", "center", "center", "center"]
        ):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor=anchor)
        # Configura los tags para colorear las filas (usando tonos pastel)
        self.tree.tag_configure("critical", background="#ffcccc", foreground="#660000")
        self.tree.tag_configure("warning", background="#ffffcc", foreground="#666600")
        self.tree.tag_configure("ok", background="#ccffcc", foreground="#006600")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ctk.CTkScrollbar(self.tree_frame, orientation="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", on_seleccion)

        ctk.CTkButton(self, text="Refrescar Lista", command=on_refrescar).pack(padx=5, pady=5)

        # Panel de cantidad
        self.cantidad_frame = ctk.CTkFrame(self)
        self.cantidad_frame.pack(padx=5, pady=5)
        self.btn_minus = ctk.CTkButton(self.cantidad_frame, text="-", command=self._decrementar, width=30)
        self.btn_minus.grid(row=0, column=0, padx=5, pady=5)
        self.entry_cantidad = ctk.CTkEntry(self.cantidad_frame, textvariable=cantidad_var, width=60)
        self.entry_cantidad.grid(row=0, column=1, padx=5, pady=5)
        self.btn_plus = ctk.CTkButton(self.cantidad_frame, text="+", command=self._incrementar, width=30)
        self.btn_plus.grid(row=0, column=2, padx=5, pady=5)

        self.btn_agregar = ctk.CTkButton(self, text="Agregar al Carrito", command=on_agregar)
        self.btn_agregar.pack(padx=5, pady=5)

        self.deshabilitar_controles()

    def obtener_termino_busqueda(self):
        return self.entry_search.get().strip()

    def cargar_productos(self, productos):
        self.tree.delete(*self.tree.get_children())
        for prod in productos:
            item = self.tree.insert("", "end", values=(
                prod["prodID"], prod["nombre"], prod["precio"], prod["stock"], prod["indicador"]
            ))
            if prod["indicador"] == "Crítico":
                self.tree.item(item, tags=("critical",))
            elif prod["indicador"] == "Preocupante":
                self.tree.item(item, tags=("warning",))
            else:
                self.tree.item(item, tags=("ok",))
        self.ajustar_ancho_columnas()

    def obtener_producto_seleccionado(self):
        item = self.tree.focus()
        if not item:
            return None
        valores = self.tree.item(item, "values")
        return {
            "prodID": valores[0],
            "nombre": valores[1],
            "precio": float(valores[2]),
            "stock": int(valores[3]),
            "indicador": valores[4]
        }

    def habilitar_controles(self):
        self.btn_minus.configure(state="normal")
        self.btn_plus.configure(state="normal")
        self.entry_cantidad.configure(state="normal")
        self.btn_agregar.configure(state="normal")

    def deshabilitar_controles(self):
        self.btn_minus.configure(state="disabled")
        self.btn_plus.configure(state="disabled")
        self.entry_cantidad.configure(state="disabled")
        self.btn_agregar.configure(state="disabled")

    def _decrementar(self):
        try:
            actual = int(self.cantidad_var.get())
        except ValueError:
            actual = 1
        if actual > 1:
            self.cantidad_var.set(str(actual - 1))

    def _incrementar(self):
        try:
            actual = int(self.cantidad_var.get())
        except ValueError:
            actual = 1
        producto = self.obtener_producto_seleccionado()
        max_stock = producto["stock"] if producto else actual
        if actual < max_stock:
            self.cantidad_var.set(str(actual + 1))

    def ajustar_ancho_columnas(self):
        # Se obtiene la fuente por defecto del sistema (TkDefaultFont)
        tree_font = tkFont.nametofont("TkDefaultFont")
        for col in self.tree["columns"]:
            max_width = tree_font.measure(col) + 10
            for item in self.tree.get_children():
                cell_text = str(self.tree.set(item, col))
                cell_width = tree_font.measure(cell_text) + 10
                if cell_width > max_width:
                    max_width = cell_width
            self.tree.column(col, width=max_width)

