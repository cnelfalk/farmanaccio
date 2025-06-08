# src/datos/migrar_vademecum.py

import os
import pandas as pd
from datos.conexion_bd import ConexionBD
from mysql.connector import Error

def migrar_vademecum(ruta_excel):
    """
    Verifica si la migración del vademecum se ha realizado (mediante un COUNT en la tabla).
    Si la tabla 'vademecum' está vacía, se lee el archivo Excel y se migran los registros.
    
    Se espera que el Excel tenga las siguientes columnas:
      - "nombre-comercial"
      - "presentacion"
      - "accion-farmacologica"
      - "principios-activos"
      - "laboratorio"
    """
    try:
        conexion = ConexionBD.obtener_conexion()
        if conexion is None:
            print("No se pudo conectar a la base de datos.")
            return
        cursor = conexion.cursor()
        cursor.execute("USE ventas_db")
        
        # Verificar si ya existen registros en la tabla vademecum
        cursor.execute("SELECT COUNT(*) FROM vademecum")
        count_result = cursor.fetchone()
        if count_result and count_result[0] > 0:
            print("Migración del vademecum ya se realizó. Se omite la migración.")
            cursor.close()
            conexion.close()
            return

    except Error as e:
        print("Error al verificar la migración en la base de datos:", e)
        return

    # Si la tabla está vacía, procedemos a migrar
    try:
        df = pd.read_excel(ruta_excel, sheet_name=0)
    except Exception as e:
        print("Error al leer el Excel:", e)
        return

    try:
        # Reabrir la conexión si fue cerrada anteriormente
        conexion = ConexionBD.obtener_conexion()
        if conexion is None:
            print("No se pudo conectar a la base de datos.")
            return
        cursor = conexion.cursor()
        cursor.execute("USE ventas_db")
    except Error as e:
        print("Error al conectar a la base de datos para migración:", e)
        return

    for index, row in df.iterrows():
        nombreComercial = row.get("nombre-comercial")
        presentacion = row.get("presentacion")
        accionFarmacologica = row.get("accion-farmacologica")
        principioActivo = row.get("principio-activo")
        laboratorio = row.get("laboratorio")
        
        # Convertir valores nulos a cadena vacía
        nombreComercial = "" if pd.isna(nombreComercial) else str(nombreComercial)
        presentacion = "" if pd.isna(presentacion) else str(presentacion)
        accionFarmacologica = "" if pd.isna(accionFarmacologica) else str(accionFarmacologica)
        principioActivo = "" if pd.isna(principioActivo) else str(principioActivo)
        laboratorio = "" if pd.isna(laboratorio) else str(laboratorio)
        
        sql_insert = """
            INSERT INTO vademecum (nombreComercial, presentacion, accionFarmacologica, principioActivo, laboratorio)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(sql_insert, (nombreComercial, presentacion, accionFarmacologica, principioActivo, laboratorio))
        except Error as e:
            print(f"Error al insertar el registro de la fila {index}: {e}")

    try:
        conexion.commit()
        print("Migración del vademecum completada exitosamente.")
    except Error as e:
        print("Error al hacer commit durante la migración:", e)
    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_excel = os.path.join(current_dir, "vademecum-marzo2025.xlsx")
    migrar_vademecum(ruta_excel)
