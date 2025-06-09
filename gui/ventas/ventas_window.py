# src/gui/ventas/ventas_window.py
import customtkinter as ctk
from tkinter import messagebox
from gui.ventas.productos_panel import PanelProductos
from gui.ventas.carrito_panel import PanelCarrito
from gui.ventas.controlador_carrito import ControladorCarrito
from logica.gestor_stock import StockManager
from logica.gestor_ventas import VentaManager
from logica.generar_factura import FacturaGenerator
from logica.generar_remito import RemitoGenerator
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
        
        self.generar_remito = ctk.BooleanVar(value=False)
        self.cliente_remito = {"nombre": "Anónimo", "direccion": "", "cuit": "", "iva": ""}
        self.fechaVencimientoRemito = None

        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        self.frame_principal.grid_columnconfigure(0, weight=1)
        self.frame_principal.grid_columnconfigure(1, weight=1)
        
        self.panel_productos = PanelProductos(
            master=self.frame_principal,
            on_buscar=self.buscar_productos,
            on_refrescar=self.cargar_productos,
            on_seleccion=self.seleccionar_producto,
            on_agregar=self.agregar_al_carrito,
            cantidad_var=self.quantity_var
        )
        self.panel_productos.grid(row=0, column=0, sticky="nsew")
        
        self.panel_carrito = PanelCarrito(
            master=self.frame_principal,
            cart_quantity_var=self.cart_quantity_var,
            on_item_selected=self.on_cart_item_selected,
            on_actualizar=self.actualizar_tree_carrito,
            on_eliminar=self.eliminar_cart_item,
            on_confirmar=self.confirmar,
            on_aplicar_descuento=self.actualizar_tree_carrito
        )
        self.panel_carrito.grid(row=0, column=1, sticky="nsew")
        
        self.frame_opciones = ctk.CTkFrame(self)
        self.frame_opciones.pack(fill="x", padx=10, pady=5)
        
        self.chk_remito = ctk.CTkCheckBox(
            self.frame_opciones,
            text="Generar Remito",
            variable=self.generar_remito,
            state="disabled"
        )
        self.chk_remito.pack(side="left", padx=5)
        
        self.btn_seleccionar_cliente = ctk.CTkButton(
            self.frame_opciones,
            text="Seleccionar Cliente para Remito",
            command=self.seleccionar_cliente
        )
        self.btn_seleccionar_cliente.pack(side="left", padx=5)
        
        self.btn_asignar_venc = ctk.CTkButton(
            self.frame_opciones,
            text="Asignar Vencimiento Remito",
            command=self.asignar_vencimiento_remito,
            state="disabled"
        )
        self.btn_asignar_venc.pack(side="left", padx=5)
        
        self.lbl_vencimiento_remito = ctk.CTkLabel(self.frame_opciones, text="Vencimiento: N/D")
        self.lbl_vencimiento_remito.pack(side="left", padx=5)
        
        self.lbl_cliente = ctk.CTkLabel(self.frame_opciones, text="Cliente: Anónimo")
        self.lbl_cliente.pack(side="left", padx=5)
        
        ctk.CTkButton(self, text="Volver", command=self.destroy).pack(pady=5)
        
        self.bind("<<DatosActualizados>>", lambda event: self.cargar_productos())
        self.cargar_productos()
        self.grab_set()

    def cargar_productos(self):
        productos = self.stock_manager.obtener_productos()
        self.panel_productos.cargar_productos(productos)
    
    def buscar_productos(self):
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
    
    def eliminar_cart_item(self):
        item = self.panel_carrito.obtener_item_seleccionado()
        if not item:
            return
        prod_id = item[0]
        self.controlador_carrito.eliminar_producto(prod_id)
        self.actualizar_tree_carrito()
    
    def confirmar(self):
        self.attributes("-disabled", True)
        try:
            if not self.controlador_carrito.carrito:
                messagebox.showerror("Error", "El carrito está vacío.")
                return
            if not Utilidades.confirmar_accion(self, "efectuar esta venta", tipo_usuario="usuario"):
                return
            
            exito, mensaje = self.venta_manager.confirmar_venta(self.controlador_carrito.carrito, parent=self)
            if exito:
                messagebox.showinfo("Éxito", mensaje, parent=self)
                carrito_actual = self.controlador_carrito.carrito.copy()
                if self.generar_remito.get():
                    if (self.cliente_remito.get("direccion") and 
                        self.cliente_remito.get("cuit") and 
                        self.cliente_remito.get("iva") and 
                        self.cliente_remito.get("nombre").lower() != "anónimo"):
                        rg = RemitoGenerator()
                        rg.generar_remito(
                            parent=self, 
                            cliente=self.cliente_remito,
                            carrito=carrito_actual,
                            fecha_vencimiento=getattr(self, "fechaVencimientoRemito", None)
                        )
                    else:
                        messagebox.showwarning("Remito no generado",
                                               "El cliente seleccionado no tiene los datos obligatorios para generar remito.",
                                               parent=self)
                self.controlador_carrito.limpiar()
                self.actualizar_tree_carrito()
                self.cargar_productos()
            else:
                messagebox.showerror("Error", mensaje, parent=self)
        finally:
            self.attributes("-disabled", False)
    
    def seleccionar_cliente(self):
        from gui.clientes_window import ClientesWindow
        ventana_clientes = ClientesWindow(self)
        ventana_clientes.grab_set()
        ventana_clientes.focus_force()
        self.wait_window(ventana_clientes)
        # Se obtiene el cliente seleccionado a través de la propiedad selected_cliente
        cliente = ventana_clientes.selected_cliente
        if cliente:
            if (cliente.get("direccion") and cliente.get("cuil") and cliente.get("iva") and 
                cliente.get("nombre").strip().lower() != "anónimo"):
                self.cliente_remito = {
                    "nombre": f"{cliente.get('nombre')} {cliente.get('apellido')}",
                    "direccion": cliente.get("direccion"),
                    "cuit": cliente.get("cuil"),
                    "iva": cliente.get("iva")
                }
                self.lbl_cliente.configure(text=f"Cliente: {self.cliente_remito['nombre']}")
                self.chk_remito.configure(state="normal")
                self.btn_asignar_venc.configure(state="normal")
            else:
                messagebox.showwarning("Cliente Incompleto",
                                       "El cliente seleccionado no tiene la información obligatoria para generar remito. Se restablecerá a 'Anónimo'.",
                                       parent=self)
                self.cliente_remito = {"nombre": "Anónimo", "direccion": "", "cuit": "", "iva": ""}
                self.lbl_cliente.configure(text="Cliente: Anónimo")
                self.chk_remito.configure(state="disabled")
                self.btn_asignar_venc.configure(state="disabled")
        else:
            messagebox.showinfo("Sin selección", "No se seleccionó ningún cliente.", parent=self)
            self.cliente_remito = {"nombre": "Anónimo", "direccion": "", "cuit": "", "iva": ""}
            self.lbl_cliente.configure(text="Cliente: Anónimo")
            self.chk_remito.configure(state="disabled")
            self.btn_asignar_venc.configure(state="disabled")
    
    def asignar_vencimiento_remito(self):
        top = ctk.CTkToplevel(self)
        top.title("Seleccionar Vencimiento Remito")
        top.geometry("250x150")
        label = ctk.CTkLabel(top, text="Seleccione Fecha de Vencimiento:")
        label.pack(pady=10)
        from tkcalendar import DateEntry
        date_entry = DateEntry(top, width=12, date_pattern="yyyy-mm-dd")
        date_entry.pack(pady=10)
        def aceptar():
            self.fechaVencimientoRemito = date_entry.get_date()
            self.lbl_vencimiento_remito.configure(text=f"Vencimiento: {self.fechaVencimientoRemito.isoformat()}")
            top.destroy()
        btn_ok = ctk.CTkButton(top, text="Aceptar", command=aceptar)
        btn_ok.pack(pady=10)

if __name__ == "__main__":
    app = VentasWindow()
    app.mainloop()
