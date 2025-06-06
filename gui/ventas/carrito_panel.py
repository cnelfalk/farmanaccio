# gui/ventas/carrito_panel.py

import customtkinter as ctk
from tkinter import ttk

class PanelCarrito(ctk.CTkFrame):
    def __init__(self, master, cart_quantity_var, on_item_selected, on_actualizar, on_eliminar, on_confirmar, on_aplicar_descuento):
        super().__init__(master, fg_color="#245332")
        self.cart_quantity_var = cart_quantity_var

        ctk.CTkLabel(self, text="Carrito de Ventas", font=("Arial", 16)).pack(padx=5, pady=5)

        # Treeview del carrito
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(padx=5, pady=5, fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Producto", "Precio Unit.", "Cantidad", "Subtotal"),
            show="headings"
        )
        for col, ancho, anchor in zip(
            ["ID", "Producto", "Precio Unit.", "Cantidad", "Subtotal"],
            [50, 200, 100, 100, 100],
            ["center", "w", "center", "center", "center"]
        ):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor=anchor)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", on_item_selected)

        self.lbl_total = ctk.CTkLabel(self, text="Total: $0.00", font=("Arial", 14))
        self.lbl_total.pack(padx=5, pady=5)

        # Panel de descuento
        frame_descuento = ctk.CTkFrame(self)
        frame_descuento.pack(padx=5, pady=5)
        ctk.CTkLabel(frame_descuento, text="Descuento (%):").grid(row=0, column=0, padx=5, pady=5)
        self.descuento_var = ctk.StringVar(value="0")
        self.entry_descuento = ctk.CTkEntry(frame_descuento, textvariable=self.descuento_var, width=60)
        self.entry_descuento.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(frame_descuento, text="Aplicar Descuento", command=on_aplicar_descuento).grid(row=0, column=2, padx=5, pady=5)

        ctk.CTkButton(self, text="Confirmar Venta", command=on_confirmar).pack(padx=5, pady=5)

        # Controles para modificar cantidades del carrito
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(padx=5, pady=5, fill="x")
        ctk.CTkLabel(control_frame, text="Modificar Cantidad:").grid(row=0, column=0, padx=5, pady=5)

        self.btn_cart_minus = ctk.CTkButton(control_frame, text="-", command=self._decrementar, width=30)
        self.btn_cart_minus.grid(row=0, column=1, padx=5, pady=5)

        self.entry_cart_quantity = ctk.CTkEntry(control_frame, textvariable=cart_quantity_var, width=60)
        self.entry_cart_quantity.grid(row=0, column=2, padx=5, pady=5)

        self.btn_cart_plus = ctk.CTkButton(control_frame, text="+", command=self._incrementar, width=30)
        self.btn_cart_plus.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkButton(control_frame, text="Actualizar", command=on_actualizar).grid(row=0, column=4, padx=5, pady=5)
        ctk.CTkButton(control_frame, text="Eliminar del Carrito", command=on_eliminar).grid(row=0, column=5, padx=5, pady=5)

        self.deshabilitar_controles()

    def actualizar_carrito(self, items):
        self.tree.delete(*self.tree.get_children())
        for item in items:
            subtotal = item["precio"] * item["cantidad"]
            self.tree.insert("", "end", values=(
                item["prodId"], item["nombre"], item["precio"], item["cantidad"], subtotal
            ))

    def actualizar_total(self, total, descuento):
        self.lbl_total.configure(text=f"Total: ${total:.2f} (Descuento: {descuento:.0f}%)")

    def obtener_item_seleccionado(self):
        item = self.tree.focus()
        if not item:
            return None
        return self.tree.item(item, "values")

    def obtener_descuento(self):
        return self.descuento_var.get()

    def habilitar_controles(self):
        self.btn_cart_minus.configure(state="normal")
        self.btn_cart_plus.configure(state="normal")
        self.entry_cart_quantity.configure(state="normal")

    def deshabilitar_controles(self):
        self.btn_cart_minus.configure(state="disabled")
        self.btn_cart_plus.configure(state="disabled")
        self.entry_cart_quantity.configure(state="disabled")
        self.cart_quantity_var.set("")

    def _decrementar(self):
        try:
            actual = int(self.cart_quantity_var.get())
        except ValueError:
            actual = 1
        self.cart_quantity_var.set(str(max(actual - 1, 1)))

    def _incrementar(self):
        try:
            actual = int(self.cart_quantity_var.get())
        except ValueError:
            actual = 1
        self.cart_quantity_var.set(str(actual + 1))