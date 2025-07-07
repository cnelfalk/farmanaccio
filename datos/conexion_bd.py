# src/datos/conexion_bd.py

import os
import mysql.connector
from mysql.connector import pooling, Error
from tkinter import messagebox

# Parámetros de conexión (sin suponer que la DB ya exista)
config_db = {
    "host":     "localhost",
    "user":     "root",
    "password": "",
    "port":     3306,
    "database": "farmanaccio_db"
}

def _ensure_database_exists():
    """
    Si la base 'farmanaccio_db' no existe, la crea conectando
    sin especificar database.
    """
    tmp_conf = {k:v for k,v in config_db.items() if k != "database"}
    conn = mysql.connector.connect(**tmp_conf)
    cur  = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {config_db['database']}")
    conn.commit()
    cur.close()
    conn.close()

# Intento de crear el pool, auto-creando la base si hace falta
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name   = "farmanaccio_pool",
        pool_size   = 5,
        **config_db
    )
except Error as err:
    # Si falla por “Unknown database”, primero la creamos
    if "Unknown database" in str(err):
        try:
            _ensure_database_exists()
            # reintentar pool
            connection_pool = pooling.MySQLConnectionPool(
                pool_name = "farmanaccio_pool",
                pool_size = 5,
                **config_db
            )
        except Exception as e2:
            messagebox.showerror(
                "Error al crear la base",
                f"No se pudo crear la base de datos:\n{e2}"
            )
            exit(1)
    else:
        messagebox.showerror(
            "Error al crear el pool",
            f"No se pudo crear el pool de conexiones.\n\n{err}"
        )
        exit(1)

class ConexionBD:
    """
    Obtiene conexiones del pool. Si algo falla, informa y retorna None.
    """
    @staticmethod
    def obtener_conexion():
        try:
            return connection_pool.get_connection()
        except Error as err:
            messagebox.showerror(
                "Error de conexión",
                f"No se pudo obtener una conexión del pool.\n\n{err}"
            )
            return None

# Prueba rápida
if __name__ == "__main__":
    cn = ConexionBD.obtener_conexion()
    if cn:
        print("¡Conexión exitosa!")
        cn.close()
