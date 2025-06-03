# src/gui/ventas_window.py
import customtkinter as ctk
import tkinter as tk
from gui.login import icono_logotipo
from tkinter import ttk, messagebox
from datetime import datetime

# Importar las clases refactorizadas en lugar de funciones libres
from logica.gestor_stock import StockManager
from logica.gestor_ventas import VentaManager
from logica.generar_factura import FacturaGenerator
from utils.utilidades import Utilidades
from mysql.connector import Error

class VentasWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Ventas - Carrito")
        self.resizable(False, False)

        # Dimensiones de la ventana
        window_width = 1300
        window_height = 525
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Carrito: lista interna para almacenar productos seleccionados
        self.carrito = []
        self.selected_product = None

        # Variables para manejo de cantidades en el ingreso y en el carrito
        self.quantity_var = ctk.StringVar(value="1")
        self.cart_quantity_var = ctk.StringVar(value="")

        # Instanciar los gestores refactorizados:
        self.stock_manager = StockManager()
        self.venta_manager = VentaManager()
        self.factura_generator = FacturaGenerator()

        # --- CONTENEDOR PRINCIPAL ---
        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.pack(padx=10, pady=10, fill="both", expand=True)
        self.frame_principal.grid_columnconfigure(0, weight=1)
        self.frame_principal.grid_columnconfigure(1, weight=1)

        # ------ IZQUIERDA: Productos Disponibles ------
        self.frame_disponibles = ctk.CTkFrame(self.frame_principal, fg_color="#408E57")
        self.frame_disponibles.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_disponibles.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self.frame_disponibles, text="Productos Disponibles", font=("Arial", 16)).pack(padx=5, pady=5)

        # --- Área de búsqueda ---
        self.search_frame = ctk.CTkFrame(self.frame_disponibles, fg_color="transparent")
        self.search_frame.pack(padx=10, pady=5, expand=True)
        self.search_frame_inside = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        self.search_frame_inside.pack(padx=5)
        self.entry_search = ctk.CTkEntry(self.search_frame_inside, width=500, placeholder_text="Buscar producto...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.btn_search = ctk.CTkButton(self.search_frame_inside, text="Buscar", command=self.buscar_productos)
        self.btn_search.pack()

        # Frame contenedor para Treeview de productos y scrollbar
        self.tree_productos_frame = ctk.CTkFrame(self.frame_disponibles)
        self.tree_productos_frame.pack(padx=5, pady=5, fill="both", expand=True)
        self.tree_productos = ttk.Treeview(
            self.tree_productos_frame,
            columns=("ID", "Producto", "Precio Unit.", "Stock"),
            show="headings"
        )
        self.tree_productos.heading("ID", text="ID")
        self.tree_productos.heading("Producto", text="Producto")
        self.tree_productos.heading("Precio Unit.", text="Precio Unit.")
        self.tree_productos.heading("Stock", text="Stock")
        self.tree_productos.column("ID", width=50, anchor="center")
        self.tree_productos.column("Producto", width=200, anchor="w")
        self.tree_productos.column("Precio Unit.", width=100, anchor="center")
        self.tree_productos.column("Stock", width=100, anchor="center")
        self.tree_productos.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_productos = ctk.CTkScrollbar(
            self.tree_productos_frame, orientation="vertical",
            command=self.tree_productos.yview
        )
        self.scrollbar_productos.grid(row=0, column=1, sticky="ns")
        self.tree_productos.configure(yscrollcommand=self.scrollbar_productos.set)
        self.tree_productos_frame.columnconfigure(0, weight=1)
        self.tree_productos_frame.rowconfigure(0, weight=1)
        self.tree_productos.bind("<<TreeviewSelect>>", self.on_product_selected)

        self.btn_refresh = ctk.CTkButton(
            self.frame_disponibles,
            text="Refrescar Lista",
            command=self.cargar_productos_disp
        )
        self.btn_refresh.pack(padx=5, pady=5)

        # Panel para ajuste de cantidad (para agregar producto al carrito)
        self.frame_cantidad = ctk.CTkFrame(self.frame_disponibles)
        self.frame_cantidad.pack(padx=5, pady=5)
        self.btn_minus = ctk.CTkButton(self.frame_cantidad, text="-", command=self.decrementar, width=30)
        self.btn_minus.grid(row=0, column=0, padx=5, pady=5)
        self.entry_cantidad = ctk.CTkEntry(self.frame_cantidad, textvariable=self.quantity_var, width=60)
        self.entry_cantidad.grid(row=0, column=1, padx=5, pady=5)
        self.btn_plus = ctk.CTkButton(self.frame_cantidad, text="+", command=self.incrementar, width=30)
        self.btn_plus.grid(row=0, column=2, padx=5, pady=5)
        self.btn_minus.configure(state="disabled")
        self.btn_plus.configure(state="disabled")
        self.entry_cantidad.configure(state="disabled")
        
        self.btn_agregar_producto = ctk.CTkButton(
            self.frame_disponibles,
            text="Agregar al Carrito",
            command=self.agregar_al_carrito,
            state="disabled"
        )
        self.btn_agregar_producto.pack(padx=5, pady=5)

        # ------ DERECHA: Carrito de Ventas ------
        self.frame_carrito = ctk.CTkFrame(self.frame_principal, fg_color="#245332")
        self.frame_carrito.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.frame_carrito.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self.frame_carrito, text="Carrito de Ventas", font=("Arial", 16)).pack(padx=5, pady=5)

        # Frame para el Treeview del carrito y scrollbar
        self.tree_carrito_frame = ctk.CTkFrame(self.frame_carrito)
        self.tree_carrito_frame.pack(padx=5, pady=5, fill="both", expand=True)
        self.tree_carrito = ttk.Treeview(
            self.tree_carrito_frame,
            columns=("ID", "Producto", "Precio Unit.", "Cantidad", "Subtotal"),
            show="headings"
        )
        self.tree_carrito.heading("ID", text="ID")
        self.tree_carrito.heading("Producto", text="Producto")
        self.tree_carrito.heading("Precio Unit.", text="Precio Unit.")
        self.tree_carrito.heading("Cantidad", text="Cantidad")
        self.tree_carrito.heading("Subtotal", text="Subtotal")
        self.tree_carrito.column("ID", width=50, anchor="center")
        self.tree_carrito.column("Producto", width=200, anchor="w")
        self.tree_carrito.column("Precio Unit.", width=100, anchor="center")
        self.tree_carrito.column("Cantidad", width=100, anchor="center")
        self.tree_carrito.column("Subtotal", width=100, anchor="center")
        self.tree_carrito.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_carrito = ctk.CTkScrollbar(
            self.tree_carrito_frame, orientation="vertical",
            command=self.tree_carrito.yview
        )
        self.scrollbar_carrito.grid(row=0, column=1, sticky="ns")
        self.tree_carrito.configure(yscrollcommand=self.scrollbar_carrito.set)
        self.tree_carrito_frame.columnconfigure(0, weight=1)
        self.tree_carrito_frame.rowconfigure(0, weight=1)
        self.tree_carrito.bind("<<TreeviewSelect>>", self.on_cart_item_selected)
        
        self.lbl_total = ctk.CTkLabel(self.frame_carrito, text="Total: $0.00", font=("Arial", 14))
        self.lbl_total.pack(padx=5, pady=5)

        # Panel de descuento
        self.frame_descuento = ctk.CTkFrame(self.frame_carrito)
        self.frame_descuento.pack(padx=5, pady=5)
        ctk.CTkLabel(self.frame_descuento, text="Descuento (%):").grid(row=0, column=0, padx=5, pady=5)
        self.descuento_var = ctk.StringVar(value="0")
        self.entry_descuento = ctk.CTkEntry(self.frame_descuento, textvariable=self.descuento_var, width=60)
        self.entry_descuento.grid(row=0, column=1, padx=5, pady=5)
        self.btn_aplicar_descuento = ctk.CTkButton(
            self.frame_descuento, text="Aplicar Descuento", command=self.actualizar_tree_carrito
        )
        self.btn_aplicar_descuento.grid(row=0, column=2, padx=5, pady=5)

        self.btn_confirmar = ctk.CTkButton(self.frame_carrito, text="Confirmar Venta", command=self.confirmar)
        self.btn_confirmar.pack(padx=5, pady=5)
        
        # Controles para modificar la cantidad en el carrito
        self.frame_cart_controls = ctk.CTkFrame(self.frame_carrito)
        self.frame_cart_controls.pack(padx=5, pady=5, fill="x")
        ctk.CTkLabel(self.frame_cart_controls, text="Modificar Cantidad:").grid(row=0, column=0, padx=5, pady=5)
        self.btn_cart_minus = ctk.CTkButton(self.frame_cart_controls, text="-", command=self.decrementar_cart, width=30)
        self.btn_cart_minus.grid(row=0, column=1, padx=5, pady=5)
        self.entry_cart_quantity = ctk.CTkEntry(self.frame_cart_controls, textvariable=self.cart_quantity_var, width=60)
        self.entry_cart_quantity.grid(row=0, column=2, padx=5, pady=5)
        self.btn_cart_plus = ctk.CTkButton(self.frame_cart_controls, text="+", command=self.incrementar_cart, width=30)
        self.btn_cart_plus.grid(row=0, column=3, padx=5, pady=5)
        self.btn_actualizar_cart = ctk.CTkButton(self.frame_cart_controls, text="Actualizar", command=self.actualizar_cart_item)
        self.btn_actualizar_cart.grid(row=0, column=4, padx=5, pady=5)
        self.btn_eliminar_cart = ctk.CTkButton(self.frame_cart_controls, text="Eliminar del Carrito", command=self.eliminar_cart_item)
        self.btn_eliminar_cart.grid(row=0, column=5, padx=5, pady=5)
        
        # Deshabilitar controles del carrito hasta que se seleccione un item
        self.desactivar_controles_cart()

        self.btn_volver = ctk.CTkButton(self, text="Volver", command=self.destroy)
        self.btn_volver.pack(padx=5, pady=5)

        # Carga inicial de productos disponibles
        self.cargar_productos_disp()

        self.grab_set()

        # Establecer ícono de la ventana tras 100 ms
        self.after(100, lambda: self.iconbitmap(icono_logotipo))
    
    def buscar_productos(self):
        """
        Filtra los productos según el término ingresado en el Entry.
        Se utiliza el método 'buscar_productos' del StockManager para obtener coincidencias.
        """
        termino = self.entry_search.get().strip()
        for i in self.tree_productos.get_children():
            self.tree_productos.delete(i)
        try:
            # Llamada a la función refactorizada
            productos = self.buscar_productos(termino)
            for producto in productos:
                self.tree_productos.insert("", "end", values=(
                    producto["prodId"], producto["nombre"], producto["precio"], producto["stock"]
                ))
        except Error as e:
            print("Error al buscar productos:", e)

    def desactivar_controles_cart(self):
        self.btn_cart_minus.configure(state="disabled")
        self.btn_cart_plus.configure(state="disabled")
        self.entry_cart_quantity.configure(state="disabled")
        self.btn_actualizar_cart.configure(state="disabled")
        self.btn_eliminar_cart.configure(state="disabled")
        self.cart_quantity_var.set("")
    
    def cargar_productos_disp(self):
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        # Obtenemos productos usando StockManager
        productos = self.stock_manager.obtener_productos()
        for prod in productos:
            self.tree_productos.insert("", "end", values=(
                prod["prodId"], prod["nombre"], prod["precio"], prod["stock"]
            ))
    
    def on_product_selected(self, event):
        seleccion = self.tree_productos.focus()
        if not seleccion:
            return
        valores = self.tree_productos.item(seleccion, "values")
        self.selected_product = {
            "prodId": valores[0],
            "nombre": valores[1],
            "precio": float(valores[2]),
            "stock": int(valores[3])
        }
        self.quantity_var.set("1")
        self.btn_minus.configure(state="normal")
        self.btn_plus.configure(state="normal")
        self.entry_cantidad.configure(state="normal")
        self.btn_agregar_producto.configure(state="normal")
    
    def decrementar(self):
        try:
            current = int(self.quantity_var.get())
        except ValueError:
            current = 1
        if current > 1:
            self.quantity_var.set(str(current - 1))
    
    def incrementar(self):
        try:
            current = int(self.quantity_var.get())
        except ValueError:
            current = 1
        if self.selected_product and current < self.selected_product["stock"]:
            self.quantity_var.set(str(current + 1))
    
    def agregar_al_carrito(self):
        if self.selected_product is None:
            messagebox.showerror("Error", "No se ha seleccionado ningún producto.")
            return
        try:
            cantidad = int(self.quantity_var.get())
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return
        if cantidad < 1:
            messagebox.showerror("Error", "La cantidad debe ser al menos 1.")
            return
        if cantidad > self.selected_product["stock"]:
            messagebox.showerror("Error", f"Cantidad excede el stock disponible ({self.selected_product['stock']}).")
            return
        # Buscar si el producto ya está en el carrito
        existente = next((item for item in self.carrito if item["prodId"] == self.selected_product["prodId"]), None)
        if existente:
            if existente["cantidad"] + cantidad > self.selected_product["stock"]:
                messagebox.showerror("Error", f"No se puede agregar esa cantidad, excede el stock ({self.selected_product['stock']}).")
                return
            existente["cantidad"] += cantidad
        else:
            self.carrito.append({
                "prodId": self.selected_product["prodId"],
                "nombre": self.selected_product["nombre"],
                "precio": self.selected_product["precio"],
                "cantidad": cantidad
            })
        self.actualizar_tree_carrito()
    
    def actualizar_tree_carrito(self):
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        total_carrito = 0.0
        for item in self.carrito:
            total_item = item["precio"] * item["cantidad"]
            self.tree_carrito.insert("", "end", values=(
                item["prodId"], item["nombre"], item["precio"], item["cantidad"], total_item
            ))
            total_carrito += total_item
        try:
            self.descuento = float(self.descuento_var.get())
            if self.descuento < 0:
                self.descuento = 0
            elif self.descuento > 100:
                self.descuento = 100
        except ValueError:
            self.descuento = 0
        self.total_con_descuento = total_carrito * (1 - self.descuento / 100)
        self.lbl_total.configure(text=f"Total: ${self.total_con_descuento:.2f} (Descuento: {self.descuento:.0f}%)")
        self.desactivar_controles_cart()
    
    def on_cart_item_selected(self, event):
        seleccion = self.tree_carrito.focus()
        if not seleccion:
            self.desactivar_controles_cart()
            return
        valores = self.tree_carrito.item(seleccion, "values")
        self.cart_quantity_var.set(str(valores[3]))
        self.btn_cart_minus.configure(state="normal")
        self.btn_cart_plus.configure(state="normal")
        self.entry_cart_quantity.configure(state="normal")
        self.btn_actualizar_cart.configure(state="normal")
        self.btn_eliminar_cart.configure(state="normal")
    
    def decrementar_cart(self):
        try:
            current = int(self.cart_quantity_var.get())
        except ValueError:
            current = 0
        if current > 1:
            self.cart_quantity_var.set(str(current - 1))
        else:
            self.cart_quantity_var.set("0")
    
    def incrementar_cart(self):
        try:
            current = int(self.cart_quantity_var.get())
        except ValueError:
            current = 1
        # Se utiliza StockManager para obtener productos
        prod = next((p for p in self.stock_manager.obtener_productos() if p["prodId"] == self.selected_product["prodId"]), None)
        max_stock = self.selected_product["stock"] if self.selected_product else current
        if current < max_stock:
            self.cart_quantity_var.set(str(current + 1))
    
    def actualizar_cart_item(self):
        seleccion = self.tree_carrito.focus()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un item del carrito para actualizar.")
            return
        try:
            nueva_cantidad = int(self.cart_quantity_var.get())
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return
        for item in self.carrito:
            if str(item["prodId"]) == str(self.tree_carrito.item(seleccion, "values")[0]):
                prod_disponible = next((p for p in self.stock_manager.obtener_productos() if str(p["prodId"]) == str(item["prodId"])), None)
                if prod_disponible and nueva_cantidad > prod_disponible["stock"]:
                    messagebox.showerror("Error", f"La cantidad no puede superar el stock disponible ({prod_disponible['stock']}).")
                    return
                if nueva_cantidad < 1:
                    self.carrito = [it for it in self.carrito if str(it["prodId"]) != str(item["prodId"])]
                else:
                    item["cantidad"] = nueva_cantidad
                break
        self.actualizar_tree_carrito()
    
    def eliminar_cart_item(self):
        seleccion = self.tree_carrito.focus()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un item del carrito para eliminar.")
            return
        item_id = self.tree_carrito.item(seleccion, "values")[0]
        self.carrito = [item for item in self.carrito if str(item["prodId"]) != str(item_id)]
        self.actualizar_tree_carrito()
    
    def confirmar(self):
        """
        Confirma la venta del carrito actual.
        Llama al método 'confirmar_venta' del VentaManager y, si la venta es exitosa, genera la factura.
        """
        if not self.carrito:
            messagebox.showerror("Error", "El carrito está vacío.")
            return
        # Llama al método 'confirmar_venta' de VentaManager
        exito, mensaje = self.venta_manager.confirmar_venta(self.carrito)
        if Utilidades.confirmar_accion(self, "efectuar esta venta", tipo_usuario="usuario"):
            if exito:
                messagebox.showinfo("Éxito", mensaje, parent=self)
                self.actualizar_tree_carrito()
                self.cargar_productos_disp()
                self.cargar_venta()
            else:
                messagebox.showerror("Error", mensaje, parent=self)
    
    def cargar_venta(self):
        """
        Guarda la venta en la base de datos y genera la factura.
        Se delega toda la lógica a FacturaGenerator.
        """
        try:
            self.factura_generator.generar_factura(self)
            messagebox.showinfo("Venta cargada", "¡Enhorabuena! La venta se ha cargado en la base de datos.", parent=self)
        except Error as e:
            messagebox.showerror("Error al cargar la venta en la base de datos:", e, parent=self)
    
    # Fin de las funciones relacionadas con el carrito y venta.

if __name__ == "__main__":
    app = VentasWindow()
    app.mainloop()