# src/utils/utilidades.py
from tkinter import messagebox

class Utilidades:
    @staticmethod
    def confirmar_accion(parent, accion: str, tipo_usuario: str = "usuario") -> bool:
        """
        Muestra una ventana de confirmación y retorna True si el usuario confirma.
        
        Parámetros:
          parent: Widget padre para la ventana de confirmación.
          accion: Texto descriptivo de la acción a confirmar.
          tipo_usuario: (Opcional) para personalizar el mensaje (por ejemplo, 'Usuario').
        
        Retorna:
          bool: True si el usuario confirma, False si no.
        """
        mensaje = f"{tipo_usuario.capitalize()}, ¿estás seguro de que querés {accion}?"
        return messagebox.askyesno("Confirmar acción", mensaje, parent=parent, default="no")
    
    @staticmethod
    def validar_producto(parent, producto) -> bool:
        """
        Valida que el diccionario 'producto' tenga:
          - Un nombre compuesto únicamente de letras, números y espacios.
          - Un precio numérico mayor a 0.
          - Un stock numérico no negativo.
        
        Parámetros:
          parent: Widget padre para mostrar los mensajes.
          producto: Diccionario con las claves 'nombre', 'precio' y 'stock'.
          
        Retorna:
          bool: True si el producto es válido, False en caso contrario.
        """
        nombre = producto.get("nombre", "")
        if not nombre.replace(" ", "").isalnum():
            messagebox.showwarning("Advertencia", "El nombre debe contener solo letras, números y espacios.", parent=parent)
            return False
        try:
            precio = float(producto.get("precio"))
            stock = int(producto.get("stock"))
        except (ValueError, TypeError):
            messagebox.showwarning("Advertencia", "El precio y el stock deben ser numéricos.", parent=parent)
            return False
        if precio <= 0:
            messagebox.showwarning("Advertencia", "El precio debe ser mayor a 0.", parent=parent)
            return False
        if stock < 0:
            messagebox.showwarning("Advertencia", "El stock no puede ser negativo.", parent=parent)
            return False
        return True

# Ejemplo de uso:
if __name__ == "__main__":
    # Simulación de uso, donde 'None' se puede usar como parent si no tienes una UI activa.
    producto_ejemplo = {"nombre": "Manzana", "precio": "1.5", "stock": "100"}
    if Utilidades.validar_producto(None, producto_ejemplo):
        print("El producto es válido.")
    else:
        print("El producto no es válido.")
        
    if Utilidades.confirmar_accion(None, "realizar la acción"):
        print("Acción confirmada.")
    else:
        print("Acción cancelada.")