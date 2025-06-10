# src/gui/main_window.py

import customtkinter as ctk
from tkinter import Toplevel, Label
from gui.login import icono_logotipo, mainwin_bg, boton_controlstock, disabledboton_controlstock, boton_gestionventas, boton_gestionclientes
from utils.utilidades import Utilidades
from PIL import Image
from customtkinter import CTkImage
from gui.options_window import OptionsWindow  # Importamos la ventana OptionsWindow

class MainWindow(ctk.CTk):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info  # Diccionario con la información del usuario (ej.: {"usuario": "admin", "role": "admin"})
        self.title("Sistema de Ventas")
        self.resizable(False, False)
        self.iconbitmap(icono_logotipo)
        
        # Configuramos el fondo (imagen y label de fondo)
        self.bg_image = CTkImage(
            Image.open(mainwin_bg),
            size=(280, 330)
        )
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

        # Dimensiones de la ventana principal
        window_width = 280
        window_height = 330
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.after(100, lambda: self.iconbitmap(icono_logotipo))

        # --- HEADER: Contenedor superior con botones de usuario y opciones ---
        self.header_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.header_frame.pack(side="top", anchor="w", pady=10, padx=10)
        
        # Función interna para truncar el texto si es demasiado largo.
        def truncar_texto(texto, longitud_maxima):
            if len(texto) > longitud_maxima:
                return texto[:longitud_maxima - 3] + "..."
            return texto

        usuario_completo = self.user_info["usuario"].title()
        usuario_mostrado = truncar_texto(usuario_completo, 10)
        
        # Botón del usuario
        self.user_button = ctk.CTkButton(
            self.header_frame,
            text=f"👤 {usuario_mostrado}",
            fg_color="#757033",
            command=self.toggle_user_menu
        )
        self.user_button.pack(side="left", padx=5, pady=5)

        # Variables para controlar el tooltip
        self._tooltip_id = None
        self.tooltip = None
        self._tooltip_delay = 500  # milisegundos de retardo

        # Función para programar la aparición del tooltip
        def schedule_tooltip(event):
            self.unschedule_tooltip()  # cancelar cualquier tooltip pendiente
            self._tooltip_id = self.user_button.after(self._tooltip_delay, show_tooltip)

        # Función que crea el tooltip (si aún no exista)
        def show_tooltip():
            if self.tooltip is not None:
                return  # Ya se mostró
            x = self.user_button.winfo_rootx() + 20
            y = self.user_button.winfo_rooty() + self.user_button.winfo_height() + 10
            self.tooltip = Toplevel(self)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry("+%d+%d" % (x, y))
            label = Label(self.tooltip, text=usuario_completo, justify='left',
                          background="#ffffe0", relief='solid', borderwidth=1,
                          font=("tahoma", 8, "normal"))
            label.pack(ipadx=5, ipady=3)

        # Función para destruir el tooltip
        def hide_tooltip(event):
            self.unschedule_tooltip()
            if self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None

        # Función para cancelar el "after" programado
        def unschedule_tooltip():
            if self._tooltip_id:
                self.user_button.after_cancel(self._tooltip_id)
                self._tooltip_id = None

        # Asignamos las funciones a los eventos del botón
        self.user_button.bind("<Enter>", schedule_tooltip)
        self.user_button.bind("<Leave>", hide_tooltip)
        self.user_button.bind("<ButtonPress>", hide_tooltip)
        # También guardamos las funciones internamente para poder llamarlas desde otras funciones
        self.unschedule_tooltip = unschedule_tooltip

        # Botón de opciones (ícono de engranaje)
        self.btn_options = ctk.CTkButton(
            self.header_frame,
            text="⚙",
            width=40,
            fg_color="#6B812E",
            command=self.abrir_opciones
        )
        self.btn_options.pack(side="left", padx=5, pady=5)

        # Menú desplegable del usuario
        self.user_menu_frame = ctk.CTkFrame(self, width=150, fg_color="#3A5747")
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
            self.btn_stock = ctk.CTkButton(self.main_frame, fg_color="#273D27", image=imagen_boton_controlstock,
                                            text="", command=self.abrir_stock, corner_radius=0)
        else:
            self.btn_stock = ctk.CTkButton(self.main_frame, fg_color="#273D27", image=imagen_disabledboton_controlstock,
                                            text="", command=self.abrir_stock, state="disabled", corner_radius=0)
        self.btn_stock.pack(pady=10, padx=10)

        imagen_boton_gestionventa = CTkImage(
            light_image=Image.open(boton_gestionventas),
            dark_image=Image.open(boton_gestionventas),
            size=(163, 38)
        )
        self.btn_ventas = ctk.CTkButton(self.main_frame, fg_color="#273D27", image=imagen_boton_gestionventa,
                                        text="", command=self.abrir_ventas, corner_radius=0)
        self.btn_ventas.pack(pady=10, padx=10)

        imagen_boton_gestionclientes = CTkImage(
            light_image=Image.open(boton_gestionclientes),
            dark_image=Image.open(boton_gestionclientes),
            size=(163, 38)
        )
        self.btn_clientes = ctk.CTkButton(self.main_frame, text="", image=imagen_boton_gestionclientes,
                                          fg_color="#273D27", command=self.abrir_clientes, corner_radius=0)
        self.btn_clientes.pack(pady=10, padx=10)

    def abrir_opciones(self):
        OptionsWindow(self)

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
            from gui.login import LoginWindow
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
        from gui.ventas.ventas_window import VentasWindow
        ventana_ventas = VentasWindow(self)
        self.wait_window(ventana_ventas)
        self.deiconify()

    def abrir_clientes(self):
        self.withdraw()
        from gui.clientes_window import ClientesWindow
        ventana_clientes = ClientesWindow(self)
        self.wait_window(ventana_clientes)
        self.deiconify()


if __name__ == "__main__":
    user_info = {"usuario": "UnUsuarioMuyLargo", "role": "admin"}
    app = MainWindow(user_info)
    app.mainloop()
