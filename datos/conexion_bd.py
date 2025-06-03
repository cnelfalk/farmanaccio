# src/datos/conexion_bd.py
import mysql.connector
import os
from mysql.connector import Error
from tkinter import messagebox

class ConexionBD:
    """
    Clase para gestionar las conexiones a la base de datos MySQL.
    Intenta conectarse a un servidor remoto y, en caso de fallo,
    intenta conectarse localmente (por ejemplo, con XAMPP).
    """

    @staticmethod
    def obtener_conexion():
        try:
            print("Conectando a conexión local (XAMPP)...")
            conexion_local = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                port=3306
            )
            print("Conexión local exitosa.")
            return conexion_local
        except Error as e_local:
            messagebox.showerror(
                "Error de conexión",
                f"No se pudo conectar localmente a MySQL.\n\n"
                f"Error local: {e_local}"
            )
            exit()
            return None

# Ejemplo de uso:
if __name__ == "__main__":
    conexion = ConexionBD.obtener_conexion()
    if conexion:
        print("Conexión establecida exitosamente.")
        conexion.close()