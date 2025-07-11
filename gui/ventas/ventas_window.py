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

        # gestores
        self.stock_manager       = StockManager()
        self.venta_manager       = VentaManager()
        self.controlador_carrito = ControladorCarrito(self.stock_manager)

        # variables
        self.quantity_var           = ctk.StringVar(value="1")
        self.cart_quantity_var      = ctk.StringVar(value="")
        self.selected_product       = None
        self.generar_remito         = ctk.BooleanVar(value=False)
        self.cliente_remito         = {
            "nombre":"", "apellido":"", "cuit":"", "iva":"", "direccion":""
        }
        self.fechaVencimientoRemito = None

        self._build_layout()
        self.cargar_productos()

    def _build_layout(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Panel Productos
        self.panel_productos = PanelProductos(
            master=frame,
            on_buscar=self.buscar_productos,
            on_refrescar=self.cargar_productos,
            on_seleccion=self.seleccionar_producto,
            on_agregar=self.agregar_al_carrito,
            cantidad_var=self.quantity_var
        )
        self.panel_productos.grid(row=0, column=0, sticky="nsew")

        # Panel Carrito
        self.panel_carrito = PanelCarrito(
            master=frame,
            cart_quantity_var=self.cart_quantity_var,
            on_item_selected=self.on_cart_item_selected,
            on_actualizar=self.actualizar_tree_carrito,
            on_eliminar=self.eliminar_cart_item,
            on_confirmar=self.confirmar,
            on_aplicar_descuento=self.actualizar_tree_carrito
        )
        self.panel_carrito.grid(row=0, column=1, sticky="nsew")

        # Cliente/Remito
        rem = ctk.CTkFrame(self, fg_color="transparent")
        rem.pack(pady=5)
        self.chk_remito = ctk.CTkCheckBox(
            rem, text="Generar Remito",
            variable=self.generar_remito, state="disabled"
        )
        self.chk_remito.grid(row=0, column=0, padx=5)
        self.btn_seleccionar_cliente = ctk.CTkButton(
            rem, text="Seleccionar Cliente",
            command=self.seleccionar_cliente
        )
        self.btn_seleccionar_cliente.grid(row=0, column=1, padx=5)
        self.btn_asignar_venc = ctk.CTkButton(
            rem, text="Asignar Vencimiento del Remito",
            command=self.asignar_vencimiento_remito, state="disabled"
        )
        self.btn_asignar_venc.grid(row=0, column=2, padx=5)
        self.lbl_venc = ctk.CTkLabel(rem, text="Vencimiento: N/D")
        self.lbl_venc.grid(row=0, column=3, padx=5)
        self.lbl_cliente = ctk.CTkLabel(rem, text="Cliente: Sin seleccionar")
        self.lbl_cliente.grid(row=0, column=4, padx=5)

        # Tipo factura + Volver
        tipo = ctk.CTkFrame(self)
        tipo.pack(pady=5)
        self.tipo_factura_var = ctk.StringVar(value="B")
        ctk.CTkLabel(tipo, text="Tipo de Factura:").pack(side="left", padx=5)
        self.combo_tipo_factura = ctk.CTkComboBox(
            tipo, values=["A","B","C"],
            variable=self.tipo_factura_var, width=80
        )
        self.combo_tipo_factura.pack(side="left", padx=5)
        ctk.CTkButton(self, text="Volver", command=self.destroy).pack(pady=10)

        self.bind("<<DatosActualizados>>", lambda e: self.cargar_productos())

    def cargar_productos(self):
        productos = self.stock_manager.obtener_productos()
        self.panel_productos.cargar_productos(productos)

    def buscar_productos(self):
        término = self.panel_productos.obtener_termino_busqueda().lower()
        todos = self.stock_manager.obtener_productos()
        filtrados = [p for p in todos if término in p["nombre"].lower()]
        self.panel_productos.cargar_productos(filtrados)

    def seleccionar_producto(self, event=None):
        self.selected_product = self.panel_productos.obtener_producto_seleccionado()
        if self.selected_product:
            self.quantity_var.set("1")
            self.panel_productos.habilitar_controles()

    def agregar_al_carrito(self):
        raw = self.quantity_var.get().replace(",",".")
        if not raw.isdigit():
            messagebox.showerror("Error","Cantidad inválida", parent=self)
            return
        qty = int(raw)
        if self.controlador_carrito.agregar_producto(self.selected_product, qty):
            self._render_carrito()
            self.panel_productos.deshabilitar_controles()

    def on_cart_item_selected(self, event=None):
        item = self.panel_carrito.obtener_item_seleccionado()
        if item:
            self.cart_quantity_var.set(str(item[3]))
            self.panel_carrito.habilitar_controles()

    def actualizar_tree_carrito(self):
        sel = self.panel_carrito.obtener_item_seleccionado()
        if not sel:
            messagebox.showerror("Error", "Seleccione un ítem del carrito.", parent=self)
            return

        prod_id = sel[0]
        old_qty = int(sel[3])
        try:
            nueva = int(self.cart_quantity_var.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida.", parent=self)
            return

        # mínima
        if nueva < 1:
            messagebox.showwarning("Atención", "La cantidad mínima es 1.", parent=self)
            return

        # tope a partir de stock almacenado en el carrito
        carro = self.controlador_carrito.carrito
        item = next((i for i in carro if i["prodID"] == prod_id), None)
        if not item:
            return
        stock_total = item["stock"]  # asumimos que ControladorCarrito guarda 'stock'

        if nueva > stock_total:
            messagebox.showwarning(
                "Atención",
                f"No puedes pedir más de {stock_total} unidades.",
                parent=self
            )
            return

        if self.controlador_carrito.actualizar_producto(prod_id, nueva):
            self._render_carrito()

    def eliminar_cart_item(self):
        item = self.panel_carrito.obtener_item_seleccionado()
        if item:
            self.controlador_carrito.eliminar_producto(item[0])
            self._render_carrito()

    def _render_carrito(self):
        total = self.controlador_carrito.aplicar_descuento(
            self.panel_carrito.obtener_descuento()
        )
        self.panel_carrito.actualizar_carrito(self.controlador_carrito.carrito)
        self.panel_carrito.actualizar_total(total, self.controlador_carrito.descuento)
        self.panel_carrito.deshabilitar_controles()

    def confirmar(self):
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

        if self.generar_remito.get():
            faltan2 = []
            if not c["direccion"].strip():      faltan2.append("Dirección")
            if not self.fechaVencimientoRemito: faltan2.append("Vencimiento")
            if faltan2:
                msg = "Faltan: "+", ".join(faltan2)+\
                      "\n¿Facturar sin remito (Sí) o cancelar (No)?"
                if messagebox.askyesno("Confirmar", msg, parent=self):
                    self.generar_remito.set(False)
                else:
                    return

        if not self.controlador_carrito.carrito:
            messagebox.showerror("Error", "El carrito está vacío.", parent=self)
            return
        if not Utilidades.confirmar_accion(self, "efectuar esta venta"):
            return

        tipo = self.tipo_factura_var.get()
        ok, msg = self.venta_manager.confirmar_venta(
            self.controlador_carrito.carrito,
            self.controlador_carrito.descuento,
            cliente=self.cliente_remito,
            tipo_factura=tipo,
            parent=self
        )
        if ok:
            messagebox.showinfo("Éxito", msg, parent=self)
            if self.generar_remito.get():
                rg = RemitoGenerator()
                rg.generar_remito(
                    parent=self,
                    cliente=self.cliente_remito,
                    carrito=self.controlador_carrito.carrito.copy(),
                    fecha_vencimiento=self.fechaVencimientoRemito
                )
            self.controlador_carrito.limpiar()
            self._render_carrito()
            self.cargar_productos()
        else:
            messagebox.showerror("Error", msg, parent=self)

    def seleccionar_cliente(self):
        from gui.clientes_window import ClientesWindow
        ventana = ClientesWindow(self)
        ventana.grab_set()
        ventana.wait_window()

        cl = ventana.selected_cliente
        if cl and cl.get("nombre") and cl.get("apellido") and cl.get("cuil") and cl.get("iva"):
            self.cliente_remito = {
                "nombre": cl["nombre"],
                "apellido": cl["apellido"],
                "cuit": cl["cuil"],
                "iva": cl["iva"],
                "direccion": cl.get("direccion", "")
            }
            self.chk_remito.configure(state="normal")
            self.btn_asignar_venc.configure(state="normal")
        else:
            messagebox.showwarning(
                "Cliente inválido",
                "Debe tener Nombre, Apellido, CUIT-CUIL e IVA.",
                parent=self
            )
            self.cliente_remito = {
                "nombre":"", "apellido":"", "cuit":"", "iva":"", "direccion":""
            }
            self.chk_remito.configure(state="disabled")
            self.btn_asignar_venc.configure(state="disabled")

        texto = f"{self.cliente_remito['nombre']} {self.cliente_remito['apellido']}".strip() or "Sin seleccionar"
        self.lbl_cliente.configure(text=f"Cliente: {texto}")

    def asignar_vencimiento_remito(self):
        top = Toplevel(self)
        top.title("Seleccionar Vencimiento Remito")
        top.geometry("250x150")
        top.iconbitmap(icono_logotipo)
        top.grab_set()

        from tkcalendar import DateEntry
        import datetime

        hoy     = datetime.date.today()
        min_date= hoy + datetime.timedelta(days=1)

        date_entry = DateEntry(
            top,
            width=12,
            date_pattern="yyyy-mm-dd",
            mindate=min_date,
            locale="es_ES"
        )
        date_entry.pack(pady=20)

        def aceptar():
            self.fechaVencimientoRemito = date_entry.get_date()
            self.lbl_vencimiento_remito.configure(
                text=f"Vencimiento: {self.fechaVencimientoRemito.isoformat()}"
            )
            top.destroy()

        ctk.CTkButton(top, text="Aceptar", command=aceptar).pack(pady=10)
        top.mainloop()
