# src/gui/ventas/ventas_window.py

import customtkinter as ctk
from tkinter import messagebox
from gui.ventas.productos_panel import PanelProductos
from gui.ventas.carrito_panel import PanelCarrito
from gui.ventas.controlador_carrito import ControladorCarrito
from logica.gestor_stock import StockManager
from logica.gestor_ventas import VentaManager
from logica.generar_factura import FacturaGenerator
from utils.utilidades import Utilidades

class VentasWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Ventas - Carrito")
        self.geometry("1300x525")
        self.resizable(False, False)

        self.stock_manager = StockManager()
        self.venta_manager = VentaManager()
        self.factura_generator = FacturaGenerator()
        self.controlador_carrito = ControladorCarrito(self.stock_manager)

        self.quantity_var = ctk.StringVar(value="1")
        self.cart_quantity_var = ctk.StringVar(value="")
        self.selected_product = None

        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        self.frame_principal.grid_columnconfigure(0, weight=1)
        self.frame_principal.grid_columnconfigure(1, weight=1)

        # Panel de productos disponibles
        self.panel_productos = PanelProductos(
            master=self.frame_principal,
            on_buscar=self.buscar_productos,
            on_refrescar=self.cargar_productos,
            on_seleccion=self.seleccionar_producto,
            on_agregar=self.agregar_al_carrito,
            cantidad_var=self.quantity_var
        )
        self.panel_productos.grid(row=0, column=0, sticky="nsew")

        # Panel del carrito
        self.panel_carrito = PanelCarrito(
            master=self.frame_principal,
            cart_quantity_var=self.cart_quantity_var,
            on_item_selected=self.on_cart_item_selected,
            on_actualizar=self.actualizar_cart_item,
            on_eliminar=self.eliminar_cart_item,
            on_confirmar=self.confirmar,
            on_aplicar_descuento=self.actualizar_tree_carrito
        )
        self.panel_carrito.grid(row=0, column=1, sticky="nsew")

        ctk.CTkButton(self, text="Volver", command=self.destroy).pack(pady=5)

        # Vinculación para refrescar productos, usando el widget raíz
        self.bind("<<DatosActualizados>>", lambda event: self.cargar_productos())

        self.cargar_productos()
        self.grab_set()

    def cargar_productos(self):
        productos = self.stock_manager.obtener_productos()
        self.panel_productos.cargar_productos(productos)

    def buscar_productos(self):
        # Se obtiene el término y se filtra la lista de productos
        termino = self.panel_productos.obtener_termino_busqueda().lower()
        productos = self.stock_manager.obtener_productos()
        productos_filtrados = [p for p in productos if termino in p["nombre"].lower()]
        self.panel_productos.cargar_productos(productos_filtrados)

    def seleccionar_producto(self, event=None):
        self.selected_product = self.panel_productos.obtener_producto_seleccionado()
        if self.selected_product:
            self.quantity_var.set("1")
            self.panel_productos.habilitar_controles()

    def agregar_al_carrito(self):
        try:
            cantidad = int(self.quantity_var.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida.")
            return
        if self.controlador_carrito.agregar_producto(self.selected_product, cantidad):
            self.actualizar_tree_carrito()
            self.panel_productos.deshabilitar_controles()

    def actualizar_tree_carrito(self):
        total = self.controlador_carrito.aplicar_descuento(self.panel_carrito.obtener_descuento())
        self.panel_carrito.actualizar_carrito(self.controlador_carrito.carrito)
        self.panel_carrito.actualizar_total(total, self.controlador_carrito.descuento)
        self.panel_carrito.deshabilitar_controles()

    def on_cart_item_selected(self, event=None):
        item = self.panel_carrito.obtener_item_seleccionado()
        if item:
            self.cart_quantity_var.set(str(item[3]))
            self.panel_carrito.habilitar_controles()

    def actualizar_cart_item(self):
        item = self.panel_carrito.obtener_item_seleccionado()
        if not item:
            return
        try:
            nueva_cantidad = int(self.cart_quantity_var.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida.")
            return
        prod_id = item[0]
        if self.controlador_carrito.actualizar_producto(prod_id, nueva_cantidad):
            self.actualizar_tree_carrito()

    def eliminar_cart_item(self):
        item = self.panel_carrito.obtener_item_seleccionado()
        if not item:
            return
        prod_id = item[0]
        self.controlador_carrito.eliminar_producto(prod_id)
        self.actualizar_tree_carrito()

    def confirmar(self):
        if not self.controlador_carrito.carrito:
            messagebox.showerror("Error", "El carrito está vacío.")
            return

        if not Utilidades.confirmar_accion(self, "efectuar esta venta", tipo_usuario="usuario"):
            return

        # Se pasa self como widget padre para diálogos en confirmar_venta
        exito, mensaje = self.venta_manager.confirmar_venta(self.controlador_carrito.carrito, parent=self)
        if exito:
            messagebox.showinfo("Éxito", mensaje, parent=self)
            self.cargar_venta()
            self.controlador_carrito.limpiar()
            self.actualizar_tree_carrito()
            self.cargar_productos()
        else:
            messagebox.showerror("Error", mensaje, parent=self)

    def cargar_venta(self):
        try:
            self.factura_generator.generar_factura(self)
            messagebox.showinfo("Venta cargada", "¡Enhorabuena! La venta se ha cargado en la base de datos.", parent=self)
        except Exception as e:
            messagebox.showerror("Error al generar la factura", str(e), parent=self)

# Ejemplo de uso:
if __name__ == "__main__":
    app = VentasWindow()
    app.mainloop()
