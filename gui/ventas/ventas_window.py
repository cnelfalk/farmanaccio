# src/gui/ventas/ventas_window.py

import customtkinter as ctk
from tkinter import messagebox, Toplevel
from gui.login import icono_logotipo
from gui.ventas.productos_panel import PanelProductos
from gui.ventas.carrito_panel import PanelCarrito
from gui.ventas.controlador_carrito import ControladorCarrito
from logica.gestor_stock import StockManager
from logica.gestor_ventas import VentaManager
from logica.generar_remito import RemitoGenerator
from utils.utilidades import Utilidades

class VentasWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Ventas - Carrito")
        self.resizable(False, False)
        self.iconbitmap(icono_logotipo)

        # Instancias de lógica
        self.stock_manager    = StockManager()
        self.venta_manager    = VentaManager()
        self.controlador_carrito = ControladorCarrito(self.stock_manager)

        # Variables auxiliares
        self.quantity_var     = ctk.StringVar(value="1")
        self.cart_quantity_var= ctk.StringVar(value="")
        self.selected_product = None

        # Cliente y remito
        self.generar_remito   = ctk.BooleanVar(value=False)
        # Diccionario que vamos a poblar desde la ventana de clientes
        self.cliente_remito   = {
            "nombre": "", "apellido": "", "cuit": "",
            "iva": "", "direccion": ""
        }
        self.fechaVencimientoRemito = None

        # ─── Layout ─────────────────────────────────────────────────────────
        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        self.frame_principal.grid_columnconfigure(0, weight=1)
        self.frame_principal.grid_columnconfigure(1, weight=1)

        # Panel de productos
        self.panel_productos = PanelProductos(
            master=self.frame_principal,
            on_buscar=self.buscar_productos,
            on_refrescar=self.cargar_productos,
            on_seleccion=self.seleccionar_producto,
            on_agregar=self.agregar_al_carrito,
            cantidad_var=self.quantity_var
        )
        self.panel_productos.grid(row=0, column=0, sticky="nsew")

        # Panel de carrito
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

        # Frame de remito/cliente
        self.frame_remito = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_remito.pack(pady=5, anchor="center")

        # Checkbox de remito
        self.chk_remito = ctk.CTkCheckBox(
            self.frame_remito,
            text="Generar Remito",
            variable=self.generar_remito,
            state="disabled"
        )
        self.chk_remito.grid(row=0, column=0, padx=5, pady=5)

        # Botón para seleccionar cliente
        self.btn_seleccionar_cliente = ctk.CTkButton(
            self.frame_remito,
            text="Seleccionar Cliente",
            command=self.seleccionar_cliente
        )
        self.btn_seleccionar_cliente.grid(row=0, column=1, padx=5, pady=5)

        # Botón para asignar vencimiento de remito
        self.btn_asignar_venc = ctk.CTkButton(
            self.frame_remito,
            text="Asignar Vencimiento del Remito",
            command=self.asignar_vencimiento_remito,
            state="disabled"
        )
        self.btn_asignar_venc.grid(row=0, column=2, padx=5, pady=5)

        self.lbl_vencimiento_remito = ctk.CTkLabel(
            self.frame_remito,
            text="Vencimiento: N/D"
        )
        self.lbl_vencimiento_remito.grid(row=0, column=3, padx=5, pady=5)

        self.lbl_cliente = ctk.CTkLabel(
            self.frame_remito,
            text="Cliente: Sin seleccionar"
        )
        self.lbl_cliente.grid(row=0, column=4, padx=5, pady=5)

        # Bind para refrescar stock tras modificaciones de lote
        self.bind("<<DatosActualizados>>", lambda e: self.cargar_productos())
        self.cargar_productos()

        # Botón Volver
        ctk.CTkButton(self, text="Volver", command=self.destroy).pack(pady=10)


    def cargar_productos(self):
        productos = self.stock_manager.obtener_productos()
        self.panel_productos.cargar_productos(productos)

    def buscar_productos(self):
        termino = self.panel_productos.obtener_termino_busqueda().lower()
        productos = self.stock_manager.obtener_productos()
        filtrados = [p for p in productos if termino in p["nombre"].lower()]
        self.panel_productos.cargar_productos(filtrados)

    def seleccionar_producto(self, event=None):
        self.selected_product = self.panel_productos.obtener_producto_seleccionado()
        if self.selected_product:
            self.quantity_var.set("1")
            self.panel_productos.habilitar_controles()

    def agregar_al_carrito(self):
        raw = self.quantity_var.get().replace(",", ".")
        if not raw.isdigit():
            messagebox.showerror("Error", "Cantidad inválida.", parent=self)
            return
        cantidad = int(raw)
        if self.controlador_carrito.agregar_producto(self.selected_product, cantidad):
            self.actualizar_tree_carrito()
            self.panel_productos.deshabilitar_controles()

    def actualizar_tree_carrito(self):
        total = self.controlador_carrito.aplicar_descuento(
            self.panel_carrito.obtener_descuento()
        )
        self.panel_carrito.actualizar_carrito(self.controlador_carrito.carrito)
        self.panel_carrito.actualizar_total(
            total,
            self.controlador_carrito.descuento
        )
        self.panel_carrito.deshabilitar_controles()

    def on_cart_item_selected(self, event=None):
        item = self.panel_carrito.obtener_item_seleccionado()
        if item:
            self.cart_quantity_var.set(str(item[3]))
            self.panel_carrito.habilitar_controles()

    def eliminar_cart_item(self):
        item = self.panel_carrito.obtener_item_seleccionado()
        if item:
            self.controlador_carrito.eliminar_producto(item[0])
            self.actualizar_tree_carrito()

    def confirmar(self):
        # Validar datos de cliente antes de facturar
        faltan = []
        c = self.cliente_remito
        if not c["nombre"].strip():   faltan.append("Nombre")
        if not c["apellido"].strip(): faltan.append("Apellido")
        if not c["cuit"].strip():     faltan.append("CUIT-CUIL")
        if not c["iva"].strip():      faltan.append("IVA")
        if faltan:
            messagebox.showerror(
                "Cliente incompleto",
                "Completa: " + ", ".join(faltan),
                parent=self
            )
            return

        # Validar remito
        if self.generar_remito.get():
            faltan2 = []
            if not c["direccion"].strip():        faltan2.append("Dirección")
            if not self.fechaVencimientoRemito:   faltan2.append("Vencimiento")
            if faltan2:
                msg = "Faltan: " + ", ".join(faltan2) + \
                      "\n¿Generar factura sin remito (Sí) o cancelar (No)?"
                if messagebox.askyesno("Confirmar", msg, parent=self):
                    self.generar_remito.set(False)
                else:
                    return

        if not self.controlador_carrito.carrito:
            messagebox.showerror("Error", "El carrito está vacío.", parent=self)
            return
        if not Utilidades.confirmar_accion(self, "efectuar esta venta"):
            return

        # ─── Aquí pasamos CLIENTE y PARENT correctamente ────────────────
        exito, mensaje = self.venta_manager.confirmar_venta(
            self.controlador_carrito.carrito,
            self.controlador_carrito.descuento,
            cliente=self.cliente_remito,   # <--- pasó el dict de cliente
            parent=self                   # <--- pasó self como parent
        )

        if exito:
            messagebox.showinfo("Éxito", mensaje, parent=self)

            # Generar remito si corresponde
            if self.generar_remito.get():
                rg = RemitoGenerator()
                rg.generar_remito(
                    parent=self,
                    cliente=self.cliente_remito,
                    carrito=self.controlador_carrito.carrito.copy(),
                    fecha_vencimiento=self.fechaVencimientoRemito
                )

            # Reinicio del carrito y refresco
            self.controlador_carrito.limpiar()
            self.actualizar_tree_carrito()
            self.cargar_productos()
        else:
            messagebox.showerror("Error", mensaje, parent=self)

    def seleccionar_cliente(self):
        from gui.clientes_window import ClientesWindow
        ventana = ClientesWindow(self)
        ventana.grab_set()
        ventana.wait_window()

        cliente = ventana.selected_cliente
        if cliente and cliente.get("nombre") and cliente.get("apellido") and cliente.get("cuil") and cliente.get("iva"):
            # Poblo mi dict con todos los campos, incluyendo dirección
            self.cliente_remito = {
                "nombre": cliente["nombre"],
                "apellido": cliente["apellido"],
                "cuit": cliente["cuil"],
                "iva": cliente["iva"],
                "direccion": cliente.get("direccion","")
            }
            self.chk_remito.configure(state="normal")
            self.btn_asignar_venc.configure(state="normal")
        else:
            messagebox.showwarning(
                "Cliente inválido",
                "Debe tener Nombre, Apellido, CUIT-CUIL e IVA.",
                parent=self
            )
            self.cliente_remito = {"nombre":"", "apellido":"", "cuit":"", "iva":"", "direccion":""}
            self.chk_remito.configure(state="disabled")
            self.btn_asignar_venc.configure(state="disabled")

        texto = (f"{self.cliente_remito['nombre']} "
                 f"{self.cliente_remito['apellido']}").strip() or "Sin seleccionar"
        self.lbl_cliente.configure(text=f"Cliente: {texto}")

    def asignar_vencimiento_remito(self):
        top = Toplevel(self)
        top.title("Seleccionar Vencimiento Remito")
        top.geometry("250x150")
        top.iconbitmap(icono_logotipo)
        top.grab_set()

        from tkcalendar import DateEntry
        date_entry = DateEntry(top, width=12, date_pattern="yyyy-mm-dd")
        date_entry.pack(pady=20)

        def aceptar():
            self.fechaVencimientoRemito = date_entry.get_date()
            self.lbl_vencimiento_remito.configure(
                text=f"Vencimiento: {self.fechaVencimientoRemito.isoformat()}"
            )
            top.destroy()

        ctk.CTkButton(top, text="Aceptar", command=aceptar).pack(pady=10)
        top.mainloop()
