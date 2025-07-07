# src/utils/utilidades.py
from tkinter import messagebox
import customtkinter as ctk

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

class CTkPromptArchivado(ctk.CTkToplevel):
    def __init__(self, parent=None, titulo="Archivar", mensaje="Motivo de archivado:"):
        super().__init__(parent)
        self.title(titulo)
        self.grab_set()
        self.resizable(False, False)
        self.resultado = None

        w, h = 400, 170
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw - w)//2, (sh - h)//2
        self.geometry(f"{w}x{h}+{x}+{y}")

        ctk.CTkLabel(self, text=mensaje, font=("Arial", 13)).pack(pady=(20, 10))
        self.entry = ctk.CTkEntry(self, placeholder_text="Ej: Producto vencido o descontinuado", width=300)
        self.entry.pack(pady=5)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(pady=15)
        ctk.CTkButton(btns, text="Cancelar", width=120, command=self.cancelar).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="Aceptar", width=120, command=self.aceptar).pack(side="left", padx=5)

        self.entry.focus()
        self.bind("<Return>", lambda e: self.aceptar())
        self.protocol("WM_DELETE_WINDOW", self.cancelar)
        self.wait_window()

    def aceptar(self):
        texto = self.entry.get().strip()
        if texto:
            self.resultado = texto
            self.destroy()

    def cancelar(self):
        self.resultado = None
        self.destroy()


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