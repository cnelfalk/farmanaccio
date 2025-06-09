# src/gui/login.py
import customtkinter as ctk
import os
from logica.gestor_usuarios import UsuarioManager  # Se importa la clase
from PIL import Image
from customtkinter import CTkImage
from CTkMessagebox import CTkMessagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUB_DIR = os.path.join(BASE_DIR, "guimedia")
icono_logotipo = os.path.join(SUB_DIR, "icono-win.ico")
login_bg = os.path.join(SUB_DIR, "login-bg.png")
login_contraseña = os.path.join(SUB_DIR, "login-contraseña.png")
login_ingresesuscredenciales = os.path.join(SUB_DIR, "login-ingresesuscredenciales.png")
login_usuario = os.path.join(SUB_DIR, "login-usuario.png")
mainwin_bg = os.path.join(SUB_DIR, "mainwin-bg.png")
boton_controlstock = os.path.join(SUB_DIR, "boton-control-de-stock.png")
disabledboton_controlstock = os.path.join(SUB_DIR, "boton-control-de-stock-deshabilitado.png")
boton_gestionventas = os.path.join(SUB_DIR, "boton-gestion-de-ventas.png")
boton_gestionclientes = os.path.join(SUB_DIR, "boton-gestion-de-clientes.png")
creditos_fondo = os.path.join(SUB_DIR, "creditos.png")

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login - Sistema de Ventas")
        self.iconbitmap(icono_logotipo)
        self.resizable(False, False)

        # Definir dimensiones de la ventana
        window_width = 345
        window_height = 280

        # Calcular la posición para centrar la ventana
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)

        # Establecer la geometría centrada
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.bg_image = CTkImage(
            Image.open(login_bg),  # Cambia esto por la ubicación real
            size=(345, 300)
        )

        # Mostrar imagen de fondo
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Imagen de fondo detrás del label "Ingrese sus credenciales"
        self.bg_credenciales = CTkImage(
            Image.open(login_ingresesuscredenciales),
            size=(190, 28)
        )
        self.lbl_title = ctk.CTkLabel(
            self, text="Ingrese sus credenciales", font=("Arial", 16, "bold"),
            image=self.bg_credenciales
        )
        self.lbl_title.pack(pady=20)

        # Imagen de fondo detrás del label "Usuario"
        self.bg_usuario = CTkImage(
            Image.open(login_usuario),
            size=(46, 28)
        )
        self.lbl_usuario = ctk.CTkLabel(self, text="Usuario:", image=self.bg_usuario)
        self.lbl_usuario.pack(pady=5)
        self.entry_usuario = ctk.CTkEntry(self)
        self.entry_usuario.pack(pady=5)

        # Imagen de fondo detrás del label "Contraseña:"
        self.bg_contra = CTkImage(
            Image.open(login_contraseña),
            size=(68, 28)
        )
        self.lbl_password = ctk.CTkLabel(self, text="Contraseña:", image=self.bg_contra)
        self.lbl_password.pack(pady=5)

        # Frame que contiene el Entry de contraseña y el botón de mostrar/ocultar
        self.password_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.password_frame.pack(pady=5)

        self.entry_password = ctk.CTkEntry(self.password_frame, show="*")
        self.entry_password.pack(side="left", padx=(0, 5))

        self.password_visible = False
        self.toggle_btn = ctk.CTkButton(self.password_frame, text="👁", width=10,
                                        command=self.toggle_password_visibility)
        self.toggle_btn.pack(side="left")

        # Botón para ingresar
        self.btn_ingresar = ctk.CTkButton(self, text="Ingresar", command=self.login)
        self.btn_ingresar.pack(pady=15)

        # Vinculamos la tecla Enter en toda la ventana para ejecutar login
        self.bind("<Return>", lambda event: self.login())

    def toggle_password_visibility(self):
        if self.entry_password.cget("show") == "*":
            self.entry_password.configure(show="")
            self.toggle_btn.configure(text="🚫")
        else:
            self.entry_password.configure(show="*")
            self.toggle_btn.configure(text="👁")

    def login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        if not usuario or not password:
            CTkMessagebox(title="Error", message="Ingrese usuario y contraseña", icon="cancel", fade_in_duration=1)
            return

        um = UsuarioManager()
        user_info = um.validar_usuario(usuario, password)
        if user_info is not None:
            self.destroy()
            from gui.main_window import MainWindow
            app = MainWindow(user_info)
            app.mainloop()
        else:
            CTkMessagebox(title="Error", message="Credenciales incorrectas", icon="cancel", fade_in_duration=1)

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
