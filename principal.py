# src/principal.py
import os
import customtkinter as ctk
from pathlib import Path
from datos.crear_tablas import TablaCreator

# Configuración del tema y apariencia de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(Path(__file__).parent / "farmanaccio-theme.json")

def principal():
    # 1. Crear la base de datos y las tablas correspondientes (incluyendo la tabla vademecum).
    creador = TablaCreator()
    creador.crear_base_de_datos_y_tablas()
    
    # 2. Ejecutar la migración del vademecum (esto se ejecutará cada vez que se inicie el sistema,
    #    pero internamente se verificará si la tabla ya tiene registros y, de ser así, se obvia)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_excel = os.path.join(current_dir, "datos", "vademecum-marzo2025.xlsx")
    from datos.migrar_vademecum import migrar_vademecum
    migrar_vademecum(ruta_excel)
    
    # 3. Iniciar la pantalla de login
    from gui.login import LoginWindow
    login = LoginWindow()
    login.mainloop()

if __name__ == "__main__":
    principal()
