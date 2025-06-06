# src/principal.py
import customtkinter as ctk
from pathlib import Path
from datos.crear_tablas import TablaCreator

# Configuración del tema y apariencia de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(Path(__file__).parent / "farmanaccio-theme.json")

def principal():
    # Crear la base de datos y tablas (productos, usuarios, etc.) usando la clase TablaCreator
    creador = TablaCreator()
    creador.crear_base_de_datos_y_tablas()
    
    # Iniciar la pantalla de login
    from gui.login import LoginWindow
    login = LoginWindow()
    login.mainloop()

if __name__ == "__main__":
    principal() 