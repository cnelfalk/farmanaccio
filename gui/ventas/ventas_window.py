# src/gui/ventas/ventas_window.py
import customtkinter as ctk
from tkinter import messagebox
from gui.login import icono_logotipo
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
        self.resizable(False, False)

        # Definir dimensiones de la ventana
        window_width = 1300
        window_height = 560

        # Calcular la posición para centrar la ventana
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
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
        
        # --- FRAME REMITO: centrado y ajustado a su contenido ---
        self.frame_remito = ctk.CTkFrame(self, fg_color="transparent")
        # Empaquetamos sin forzar el fill para que el frame se ajuste al contenido
        self.frame_remito.pack(pady=5, anchor="center")
        # Configuramos la grilla sin expansión de columnas
        for i in range(5):
            self.frame_remito.grid_columnconfigure(i, weight=0)

        self.chk_remito = ctk.CTkCheckBox(
            self.frame_remito,
            text="Generar Remito",
            variable=self.generar_remito,
            state="disabled"
        )
        self.chk_remito.grid(row=0, column=0, padx=5, pady=5)
        
        self.btn_seleccionar_cliente = ctk.CTkButton(
            self.frame_remito,
            text="Seleccionar Cliente para Remito",
            command=self.seleccionar_cliente
        )
        self.btn_seleccionar_cliente.grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_asignar_venc = ctk.CTkButton(
            self.frame_remito,
            text="Asignar Vencimiento Remito",
            command=self.asignar_vencimiento_remito,
            state="disabled"
        )
        self.btn_asignar_venc.grid(row=0, column=2, padx=5, pady=5)
        
        self.lbl_vencimiento_remito = ctk.CTkLabel(self.frame_remito, text="Vencimiento: N/D")
        self.lbl_vencimiento_remito.grid(row=0, column=3, padx=5, pady=5)
        
        self.lbl_cliente = ctk.CTkLabel(self.frame_remito, text="Cliente: Anónimo")
        self.lbl_cliente.grid(row=0, column=4, padx=5, pady=5)
        # --- FIN FRAME REMITO ---
        
        ctk.CTkButton(self, text="Volver", command=self.destroy).pack(pady=10)
        
        self.bind("<<DatosActualizados>>", lambda event: self.cargar_productos())
        self.cargar_productos()
        self.grab_set()
        self.after(201, lambda: self.iconbitmap(icono_logotipo))

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
        # Antes de generar la factura, si el usuario quiere generar remito, verificamos si faltan datos.
        if self.generar_remito.get():
            campos_faltantes = []
            # Verificar en el cliente seleccionado (self.cliente_remito)
            if not self.cliente_remito.get("iva"):
                campos_faltantes.append("IVA")
            if not self.cliente_remito.get("direccion"):
                campos_faltantes.append("Dirección")
            if not self.cliente_remito.get("cuit"):
                campos_faltantes.append("CUIT-CUIL")
            if not self.fechaVencimientoRemito:
                campos_faltantes.append("Fecha de vencimiento")
            if campos_faltantes:
                mensaje = (
                    "Faltan los siguientes datos para generar el remito: " +
                    ", ".join(campos_faltantes) +
                    "\n\n¿Generar factura sin remito (Sí) o cancelar la venta (No)?"
                )
                respuesta = messagebox.askyesno("Confirmar acción", mensaje, parent=self)
                if respuesta:
                    # Si el usuario acepta, desactivamos lo de remito
                    self.generar_remito.set(False)
                else:
                    return

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
                    rg = RemitoGenerator()
                    rg.generar_remito(
                        parent=self,
                        cliente=self.cliente_remito,
                        carrito=carrito_actual,
                        fecha_vencimiento=getattr(self, "fechaVencimientoRemito", None)
                    )
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

        window_width = 900
        window_height = 570
        screen_width = ventana_clientes.winfo_screenwidth()
        screen_height = ventana_clientes.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        ventana_clientes.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.wait_window(ventana_clientes)
        cliente = ventana_clientes.selected_cliente
        if cliente:
            if (cliente.get("direccion") and cliente.get("cuit") and cliente.get("iva") and 
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
        top.iconbitmap(icono_logotipo)
        top.grab_set()
        label = ctk.CTkLabel(top, text="Seleccione Fecha de Vencimiento:")
        label.pack(pady=10)
        top.after(201, lambda: self.iconbitmap(icono_logotipo))
        from tkcalendar import DateEntry
        date_entry = DateEntry(top, width=12, date_pattern="yyyy-mm-dd")
        date_entry.pack(pady=10)
        def aceptar():
            self.fechaVencimientoRemito = date_entry.get_date()
            self.lbl_vencimiento_remito.configure(text=f"Vencimiento: {self.fechaVencimientoRemito.isoformat()}")
            top.destroy()
        btn_ok = ctk.CTkButton(top, text="Aceptar", command=aceptar)
        btn_ok.pack(pady=10)
        top.after(201, lambda: self.iconbitmap(icono_logotipo))

if __name__ == "__main__":
    app = VentasWindow()
    app.mainloop()
