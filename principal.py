# src/principal.py
from datos.crear_tablas import TablaCreator

def principal():
    # Crear la base de datos y tablas (productos, usuarios, etc.) usando la clase TablaCreator
    creador = TablaCreator()
    creador.crear_base_de_datos_y_tablas()

if __name__ == "__main__":
    principal()