# gui/ventas/controlador_carrito.py

import tkinter.messagebox as messagebox

class ControladorCarrito:
    def __init__(self, stock_manager):
        self.carrito = []
        self.stock_manager = stock_manager
        self.descuento = 0.0

    def agregar_producto(self, producto, cantidad):
        """
        Añade {prodID, nombre, precio, cantidad, stock} al carrito.
        """
        if not producto:
            messagebox.showerror("Error", "No hay producto seleccionado.")
            return False
        if cantidad < 1:
            messagebox.showerror("Error", "La cantidad debe ser al menos 1.")
            return False
        if cantidad > producto["stock"]:
            messagebox.showerror(
                "Error",
                f"Excede stock disponible ({producto['stock']})."
            )
            return False

        # Buscamos si ya existe
        existente = next((i for i in self.carrito if i["prodID"] == producto["prodID"]), None)
        if existente:
            # sumamos cantidades
            nueva = existente["cantidad"] + cantidad
            if nueva > producto["stock"]:
                messagebox.showerror(
                    "Error",
                    f"No puede sumar esa cantidad (stock {producto['stock']})."
                )
                return False
            existente["cantidad"] = nueva
        else:
            # AGREGAMOS campo 'stock' aquí
            self.carrito.append({
                "prodID": producto["prodID"],
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "cantidad": cantidad,
                "stock": producto["stock"]    # <--- stock almacenado
            })
        return True

    def actualizar_producto(self, prod_id, nueva_cantidad):
        for item in self.carrito:
            if item["prodID"] == prod_id:
                # Actualizamos en base al 'stock' guardado
                stock = item.get("stock", 0)
                if nueva_cantidad > stock:
                    messagebox.showerror(
                        "Error",
                        f"No puede superar stock ({stock})."
                    )
                    return False
                if nueva_cantidad < 1:
                    self.eliminar_producto(prod_id)
                else:
                    item["cantidad"] = nueva_cantidad
                return True
        return False

    def eliminar_producto(self, prod_id):
        self.carrito = [i for i in self.carrito if i["prodID"] != prod_id]

    def calcular_total(self):
        bruto = sum(i["precio"] * i["cantidad"] for i in self.carrito)
        neto = bruto * (1 - self.descuento / 100)
        return round(neto, 2)

    def aplicar_descuento(self, valor):
        """
        Acepta valor con coma o punto, guarda self.descuento como float (con decimales),
        y devuelve el total ya descontado.
        """
        try:
            texto = str(valor).replace(",", ".")
            v = float(texto)
        except ValueError:
            messagebox.showerror("Error", "Descuento inválido. Usa números (coma o punto).")
            v = 0.0
        # Limitar entre 0 y 100
        if v < 0:
            v = 0.0
        elif v > 100:
            v = 100.0
        self.descuento = v
        return self.calcular_total()

    def obtener_descuento_str(self):
        """
        Retorna el descuento en porcentaje formateado con dos decimales, 
        e.g. "35.50".
        """
        return f"{self.descuento:.2f}"

    def limpiar(self):
        self.carrito.clear()
        self.descuento = 0.0
