# src/gui/main_window.py
import customtkinter as ctk
from gui.login import icono_logotipo, mainwin_bg, boton_controlstock, disabledboton_controlstock, boton_gestionventas
from gui.stock_window import StockWindow
from gui.ventas_window import VentasWindow
from gui.login import LoginWindow  # Para volver a mostrar el login
from gui.form_agregar_usuario import FormAgregarUsuario
from utils.utilidades import Utilidades
from PIL import Image
from customtkinter import CTkImage

class MainWindow(ctk.CTk):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info  # Diccionario con los datos del usuario (ej.: {"usuario": "admin", "role": "admin"})
        self.title("Sistema de Ventas")
        self.resizable(False, False)
        self.iconbitmap(icono_logotipo)

        # Definir dimensiones de la ventana
        window_width = 280
        window_height = 330

        # Calcular la posición para centrar la ventana
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        
        # Establecer la geometría centrada
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Establecer el ícono tras 100ms
        self.after(100, lambda: self.iconbitmap(icono_logotipo))
        
        # --- FONDO: Imagen de fondo para la ventana ---
        self.bg_image = CTkImage(
            Image.open(mainwin_bg),  # Cambia esto por el path real
            size=(280, 330)
        )
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # --- HEADER: Frame superior con el "botón" de usuario ---
        self.header_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.header_frame.pack(side="top", anchor="w", pady=10, padx=10)
        
        self.user_button = ctk.CTkButton(
            self.header_frame,
            text=f"👤 {self.user_info['usuario'].title()}",
            fg_color="#99945E",
            command=self.toggle_user_menu
        )
        self.user_button.pack(side="left", padx=5, pady=5)
        
        # Menú desplegable del usuario
        self.user_menu_frame = ctk.CTkFrame(self, width=150, fg_color="#3A5747")
        
        # Si el rol es admin, se muestran botones adicionales
        if self.user_info["role"] == "admin":
            self.btn_menu_agregar = ctk.CTkButton(
                self.user_menu_frame,
                text="(+) Agregar usuario",
                command=self.agregar_usuario,
                fg_color="#6B812E"
            )
            self.btn_menu_agregar.pack(fill="x", padx=5, pady=5)
            
            self.btn_menu_admin_usuarios = ctk.CTkButton(
                self.user_menu_frame,
                text="⚙️ Administrar usuarios",
                command=self.abrir_admin_usuarios,
                fg_color="#6B812E"
            )
            self.btn_menu_admin_usuarios.pack(fill="x", padx=5, pady=5)
        
        self.btn_menu_logout = ctk.CTkButton(
            self.user_menu_frame,
            text="Cerrar sesión",
            command=self.cerrar_sesion,
            width=5,
            fg_color="#6B812E"
        )
        self.btn_menu_logout.pack(fill="x", padx=5, pady=5)
        
        self.user_menu_frame.place_forget()
        
        # --- MAIN AREA: Botones para acceder a otras funciones ---
        self.main_frame = ctk.CTkFrame(self, fg_color="#273D27", corner_radius=15)
        self.main_frame.place(x=44, y=70)
        
        self.header_frame.lift()
        self.main_frame.lift()
        
        imagen_boton_controlstock = CTkImage(
            light_image=Image.open(boton_controlstock),
            dark_image=Image.open(boton_controlstock),
            size=(163, 38)
        )
        imagen_disabledboton_controlstock = CTkImage(
            light_image=Image.open(disabledboton_controlstock),
            dark_image=Image.open(disabledboton_controlstock),
            size=(163, 38)
        )
        
        if self.user_info["role"] == "admin":
            self.btn_stock = ctk.CTkButton(self.main_frame, fg_color="#273D27", image=imagen_boton_controlstock, text="", command=self.abrir_stock, corner_radius=0)
        else:
            self.btn_stock = ctk.CTkButton(self.main_frame, fg_color="#273D27", image=imagen_disabledboton_controlstock, text="", command=self.abrir_stock, state="disabled", corner_radius=0)
        self.btn_stock.pack(pady=10, padx=10)
        
        imagen_boton_gestionventa = CTkImage(
            light_image=Image.open(boton_gestionventas),
            dark_image=Image.open(boton_gestionventas),
            size=(163, 38)
        )
        self.btn_ventas = ctk.CTkButton(self.main_frame, fg_color="#273D27", image=imagen_boton_gestionventa, text="", command=self.abrir_ventas, corner_radius=0)
        self.btn_ventas.pack(pady=10, padx=10)
        
    def abrir_admin_usuarios(self):
        from gui.admin_usuarios_window import AdminUsuariosWindow
        AdminUsuariosWindow(self, self.user_info["usuario"])
        
    def toggle_user_menu(self):
        if self.user_menu_frame.winfo_viewable():
            self.user_menu_frame.place_forget()
        else:
            x = self.user_button.winfo_rootx() - self.winfo_rootx()
            y = self.user_button.winfo_rooty() - self.winfo_rooty() + self.user_button.winfo_height()
            self.user_menu_frame.place(x=x, y=y)
            self.user_menu_frame.lift()
        
    def agregar_usuario(self):
        from gui.form_agregar_usuario import FormAgregarUsuario
        FormAgregarUsuario(self)
        
    def cerrar_sesion(self):
        if Utilidades.confirmar_accion(self, "cerrar la sesión", tipo_usuario="usuario"):
            self.destroy()
            from gui.login import LoginWindow  # Para volver al login
            login = LoginWindow()
            login.mainloop()
        
    def abrir_stock(self):
        self.withdraw()
        from gui.stock_window import StockWindow
        ventana_stock = StockWindow(self)
        self.wait_window(ventana_stock)
        self.deiconify()
        
    def abrir_ventas(self):
        self.withdraw()
        from gui.ventas_window import VentasWindow
        ventana_ventas = VentasWindow(self)
        self.wait_window(ventana_ventas)
        self.deiconify()
        
# Ejemplo de uso:
if __name__ == "__main__":
    # Se simula un usuario logueado, por ejemplo:
    user_info = {"usuario": "admin", "role": "admin"}
    app = MainWindow(user_info)
    app.mainloop()