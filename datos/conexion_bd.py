# src/datos/conexion_bd.py
import os
from mysql.connector import pooling, Error
from tkinter import messagebox

# Configuración de la base de datos; asegúrate de poner aquí todos los parámetros necesarios
config_db = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "port": 3306,
    "database": "farmanaccio_db"
}

# Creamos un pool de conexiones con un tamaño definido (por ejemplo, 5 conexiones)
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="farmanaccio_pool",
        pool_size=5,
        **config_db
    )
except Error as err:
    messagebox.showerror(
        "Error al crear el pool",
        f"No se pudo crear el pool de conexiones.\n\nError: {err}"
    )
    exit()

class ConexionBD:
    """
    Clase para gestionar las conexiones a la base de datos MySQL utilizando un pool.
    De esta forma, en lugar de crear y destruir una conexión en cada operación,
    se obtiene una conexión del pool y al cerrarla se devuelve al mismo.
    """
    @staticmethod
    def obtener_conexion():
        try:
            return connection_pool.get_connection()
        except Error as err:
            messagebox.showerror(
                "Error de conexión",
                f"No se pudo obtener una conexión del pool.\n\nError: {err}"
            )
            return None

# Ejemplo de uso:
if __name__ == "__main__":
    conexion = ConexionBD.obtener_conexion()
    if conexion:
        print("Conexión establecida exitosamente desde el pool.")
        # Al llamar a .close() se devuelve la conexión al pool, sin cerrarla realmente.
        conexion.close()
