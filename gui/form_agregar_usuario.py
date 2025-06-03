# src/gui/form_agregar_usuario.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
from gui.login import icono_logotipo
from customtkinter import CTkToplevel
from logica.gestor_usuarios import UsuarioManager  # Se importa la clase

class FormAgregarUsuario(CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Agregar nuevo usuario")
        self.resizable(False, False)

        # Definir dimensiones de la ventana
        window_width = 300
        window_height = 280

        # Calcular la posición para centrar la ventana
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)

        # Establecer la geometría centrada
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.label_nombre = ctk.CTkLabel(self, text="Nombre de usuario:")
        self.label_nombre.pack(pady=5)
        self.entry_nombre = ctk.CTkEntry(self)
        self.entry_nombre.pack(pady=5)

        self.password_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.password_frame.pack(pady=5)

        self.label_password = ctk.CTkLabel(self.password_frame, text="Contraseña:")
        self.label_password.pack(pady=5)
        self.entry_password = ctk.CTkEntry(self.password_frame, show="*")
        self.entry_password.pack(side="left", pady=5)

        self.password_visible = False
        self.toggle_btn = ctk.CTkButton(
            self.password_frame,
            text="👁",
            width=10,
            command=self.toggle_password_visibility
        )
        self.toggle_btn.pack(side="left")

        self.label_rol = ctk.CTkLabel(self, text="Rol:")
        self.label_rol.pack(pady=3)
        self.combo_rol = ctk.CTkComboBox(self, values=["admin", "empleado"])
        self.combo_rol.pack(pady=3)
        self.combo_rol.set("empleado")  # Valor predeterminado

        self.boton_guardar = ctk.CTkButton(self, text="Guardar", command=self.guardar_usuario)
        self.boton_guardar.pack(pady=10)

        self.grab_set()

        # Aseguramos que se establezca el ícono con iconbitmap tras 175ms
        self.after(175, lambda: self.iconbitmap(icono_logotipo))

        # Instanciar UsuarioManager para manejar la creación de usuarios
        self.usuario_manager = UsuarioManager()

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.entry_password.configure(show="")
            self.toggle_btn.configure(text="🚫")
        else:
            self.entry_password.configure(show="*")
            self.toggle_btn.configure(text="👁")

    def guardar_usuario(self):
        usuario = self.entry_nombre.get()
        password = self.entry_password.get()
        rol = self.combo_rol.get().strip().lower()

        if len(password) < 5:
            messagebox.showwarning("Atención", "Asegúrese que la contraseña no sea menor a cinco carácteres.", parent=self)
            return

        if not usuario or not password or not rol:
            messagebox.showwarning("Atención", "Todos los campos son obligatorios.", parent=self)
            return

        if rol not in ("admin", "empleado"):
            messagebox.showwarning("Rol inválido", "El rol debe ser 'admin' o 'empleado'.", parent=self)
            return

        # Llamamos al método de la clase para crear el usuario
        exito = self.usuario_manager.crear_usuario(usuario, password, rol)
        if exito:
            messagebox.showinfo("Éxito", "Usuario agregado correctamente.", parent=self)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo agregar el usuario.", parent=self)

# Ejemplo de uso:
if __name__ == "__main__":
    app = FormAgregarUsuario(None)
    app.mainloop()