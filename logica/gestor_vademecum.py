# src/logica/gestor_vademecum.py
from datos.conexion_bd import ConexionBD
from mysql.connector import Error

class VademecumManager:
    def obtener_vademecum(self):
        """
        Retorna una lista de diccionarios con todos los registros de la tabla vademecum.
        Cada registro contiene: vademecumID, nombreComercial, presentacion,
        accionFarmacologica, principioActivo y laboratorio.
        """
        registros = []
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return registros
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE ventas_db")
            cursor.execute("""
                SELECT vademecumID, nombreComercial, presentacion, 
                       accionFarmacologica, principioActivo, laboratorio 
                FROM vademecum
            """)
            registros = cursor.fetchall()
            cursor.close()
            conexion.close()
        except Error as e:
            print("Error al obtener registros del vademecum:", e)
        return registros

    def buscar_vademecum(self, termino):
        """
        Retorna una lista de registros de la tabla vademecum en los que la columna
        'nombreComercial' contenga el 'termino' (busqueda insensible a mayúsculas).
        """
        registros = []
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return registros
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE ventas_db")
            sql = """
                SELECT vademecumID, nombreComercial, presentacion, 
                       accionFarmacologica, principioActivo, laboratorio 
                FROM vademecum
                WHERE LOWER(nombreComercial) LIKE %s
            """
            parametro = "%" + termino.lower() + "%"
            cursor.execute(sql, (parametro,))
            registros = cursor.fetchall()
            cursor.close()
            conexion.close()
        except Error as e:
            print("Error al buscar en el vademecum:", e)
        return registros
