# src/gui/options_window.py

import customtkinter as ctk
from gui.login import icono_logotipo  # Se usa el ícono que ya figura en login

class OptionsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Opciones")
        self.resizable(False, False)
        self.grab_set()  # Modal
        self.geometry("400x200")
        self.iconbitmap(icono_logotipo)  # Usamos el ícono definido en login

        # Frame principal
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Label con texto grande "Gestión de Ventas"
        self.lbl_titulo = ctk.CTkLabel(frame, text="Gestión de Ventas", font=("Arial", 24, "bold"))
        self.lbl_titulo.pack(pady=(0,20))
        
        # Botón que alterna entre los dos estados:
        # "Descontar stock del lote con la fecha más próxima a vencer"
        # y "Elegir manualmente de cuál lote descontar"
        self.btn_toggle = ctk.CTkButton(frame, text="", command=self.toggle_estilo, width=350)
        self.btn_toggle.pack(pady=10)
        
        self.actualizar_texto_boton()
        
    def toggle_estilo(self):
        # Importamos el módulo de configuración para cambiar el valor global
        import config
        config.manual_lote_selection = not config.manual_lote_selection
        self.actualizar_texto_boton()
        
    def actualizar_texto_boton(self):
        from config import manual_lote_selection
        if manual_lote_selection:
            self.btn_toggle.configure(text="Elegir manualmente de cuál lote descontar")
        else:
            self.btn_toggle.configure(text="Descontar stock del lote con la fecha más próxima a vencer")
