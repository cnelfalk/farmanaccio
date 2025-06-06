# gui/ventas/controlador_carrito.py

from tkinter import messagebox

class ControladorCarrito:
    def __init__(self, stock_manager):
        self.carrito = []
        self.stock_manager = stock_manager
        self.total_con_descuento = 0.0
        self.descuento = 0.0

    def agregar_producto(self, producto, cantidad):
        if not producto:
            messagebox.showerror("Error", "No se ha seleccionado ningún producto.")
            return False

        if cantidad < 1:
            messagebox.showerror("Error", "La cantidad debe ser al menos 1.")
            return False

        if cantidad > producto["stock"]:
            messagebox.showerror("Error", f"Cantidad excede el stock disponible ({producto['stock']}).")
            return False

        existente = next((item for item in self.carrito if item["prodId"] == producto["prodId"]), None)
        if existente:
            if existente["cantidad"] + cantidad > producto["stock"]:
                messagebox.showerror("Error", f"No se puede agregar esa cantidad, excede el stock ({producto['stock']}).")
                return False
            existente["cantidad"] += cantidad
        else:
            self.carrito.append({
                "prodId": producto["prodId"],
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "cantidad": cantidad
            })
        return True

    def actualizar_producto(self, prod_id, nueva_cantidad):
        for item in self.carrito:
            if str(item["prodId"]) == str(prod_id):
                producto_actual = next((p for p in self.stock_manager.obtener_productos() if str(p["prodId"]) == str(prod_id)), None)
                if producto_actual and nueva_cantidad > producto_actual["stock"]:
                    messagebox.showerror("Error", f"La cantidad no puede superar el stock disponible ({producto_actual['stock']}).")
                    return False
                if nueva_cantidad < 1:
                    self.eliminar_producto(prod_id)
                else:
                    item["cantidad"] = nueva_cantidad
                return True
        return False

    def eliminar_producto(self, prod_id):
        self.carrito = [item for item in self.carrito if str(item["prodId"]) != str(prod_id)]

    def calcular_total(self):
        total = sum(item["precio"] * item["cantidad"] for item in self.carrito)
        self.total_con_descuento = total * (1 - self.descuento / 100)
        return round(self.total_con_descuento, 2)

    def aplicar_descuento(self, valor):
        try:
            valor = float(valor)
            if valor < 0:
                valor = 0
            elif valor > 100:
                valor = 100
        except ValueError:
            valor = 0
        self.descuento = valor
        return self.calcular_total()

    def limpiar(self):
        self.carrito.clear()
        self.total_con_descuento = 0.0
        self.descuento = 0.0
