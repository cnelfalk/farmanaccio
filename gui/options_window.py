# src/gui/options_window.py

import customtkinter as ctk
from gui.login import icono_logotipo  # Se usa el mismo ícono de login
from tkinter import StringVar

class OptionsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Opciones")
        self.resizable(False, False)
        self.grab_set()  # Modal
        self.iconbitmap(icono_logotipo)

        # Dimensiones de la ventana principal
        window_width = 450
        window_height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Frame principal con márgenes
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Título con suficiente espacio superior e inferior
        self.lbl_titulo = ctk.CTkLabel(main_frame, text="Gestión de Ventas", font=("Arial", 24, "bold"))
        self.lbl_titulo.pack(pady=(20, 20))

        # Variable para controlar la opción seleccionada
        self.opcion_var = StringVar(value="Automático")

        # Botones de radio para la selección
        self.radio_manual = ctk.CTkRadioButton(
            main_frame,
            text="Manual",
            variable=self.opcion_var,
            value="Manual",
            command=self.actualizar_opcion
        )
        self.radio_manual.pack(pady=5)

        self.radio_automatico = ctk.CTkRadioButton(
            main_frame,
            text="Automático",
            variable=self.opcion_var,
            value="Automático",
            command=self.actualizar_opcion
        )
        self.radio_automatico.pack(pady=5)

        # Inicializamos el estado de acuerdo a la configuración actual
        from config import manual_lote_selection
        if manual_lote_selection:
            self.opcion_var.set("Manual")
        else:
            self.opcion_var.set("Automático")

        # Frame informativo con fondo marrón y texto en blanco
        info_frame = ctk.CTkFrame(main_frame, fg_color="#8B4513")
        info_frame.pack(fill="x", pady=10)
        info_label = ctk.CTkLabel(
            info_frame,
            text=("• Manual: Elegir manualmente de cuál lote descontar   • Automático: Descontar stock del lote con la fecha más próxima a vencer"),
            text_color="white",
            font=("Arial", 10),
            wraplength=400
        )
        info_label.pack(padx=10, pady=10)

        # Botón "Volver" para cerrar la ventana
        self.btn_volver = ctk.CTkButton(main_frame, text="Volver", command=self.destroy)
        self.btn_volver.pack(pady=10)

        self.after(201, lambda: self.iconbitmap(icono_logotipo))

    def actualizar_opcion(self):
        import config
        if self.opcion_var.get() == "Manual":
            config.manual_lote_selection = True
        else:
            config.manual_lote_selection = False

# Ejemplo de uso:
if __name__ == "__main__":
    app = OptionsWindow(None)
    app.mainloop()
