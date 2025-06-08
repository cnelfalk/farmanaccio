# src/logica/gestor_inventario.py
from datos.conexion_bd import ConexionBD
from mysql.connector import Error

class GestorInventario:
    def obtener_inventario_agrupado(self) -> list:
        """
        Retorna un resumen del inventario agrupado por producto a partir de los registros
        en la tabla lotes_productos, pero solo para productos activos (activo = 1).
        
        Cada registro resultante incluye:
          - prodId: Identificador del producto.
          - nombre: Nombre del producto.
          - precio: Precio (tomado de la tabla productos).
          - total_stock: Suma de la cantidad_disponible de todos los lotes del producto.
          - vencimiento_proximo: La fecha de vencimiento más temprana entre los lotes con stock.
        
        Solo se incluyen aquellos lotes con cantidad_disponible > 0 y solo productos activos.
        """
        inventario = []
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return inventario
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE ventas_db")
            sql = """
                SELECT 
                    p.prodId, 
                    p.nombre, 
                    p.precio,
                    SUM(l.cantidad_disponible) AS total_stock,
                    MIN(l.vencimiento) AS vencimiento_proximo
                FROM productos p
                JOIN lotes_productos l ON p.prodId = l.prodId
                WHERE p.activo = 1 AND l.cantidad_disponible > 0
                GROUP BY p.prodId, p.nombre, p.precio
            """
            cursor.execute(sql)
            inventario = cursor.fetchall()
            cursor.close()
            conexion.close()
        except Error as e:
            print("Error al obtener inventario agrupado:", e)
        return inventario

    def obtener_detalles_generales_producto(self, nombre_producto: str) -> dict:
        """
        Consulta la tabla vademecum (u otra fuente) para buscar los detalles generales 
        del producto según su nombre. Retorna un diccionario con:
          - presentacion, 
          - accionFarmacologica, 
          - principioActivo, 
          - laboratorio.
        
        Si no se encuentra, se retornan valores "No Disponible".
        """
        detalles = {}
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return {"presentacion": "No Disponible", "accionFarmacologica": "No Disponible",
                        "principioActivo": "No Disponible", "laboratorio": "No Disponible"}
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE ventas_db")
            sql = """
                SELECT presentacion, accionFarmacologica, principioActivo, laboratorio 
                FROM vademecum 
                WHERE LOWER(nombreComercial) = LOWER(%s) 
                LIMIT 1
            """
            cursor.execute(sql, (nombre_producto,))
            resultado = cursor.fetchone()
            if resultado:
                detalles = resultado
            else:
                detalles = {"presentacion": "No Disponible", "accionFarmacologica": "No Disponible",
                            "principioActivo": "No Disponible", "laboratorio": "No Disponible"}
            cursor.close()
            conexion.close()
        except Exception as e:
            detalles = {"presentacion": "No Disponible", "accionFarmacologica": "No Disponible",
                        "principioActivo": "No Disponible", "laboratorio": "No Disponible"}
        return detalles

    def obtener_detalle_lotes(self, prodId: int) -> list:
        """
        Retorna una lista de diccionarios con el detalle de los lotes para un producto específico,
        identificado por su prodId. Cada registro contiene:
          - loteID: Identificador único del registro.
          - numeroLote: Número o identificador de lote.
          - fechaIngreso: Fecha de ingreso del lote.
          - vencimiento: Fecha de vencimiento del lote.
          - cantidad_ingresada: Cantidad total ingresada en el lote.
          - cantidad_disponible: Cantidad disponible actualmente en el lote.
          
        Los registros se ordenan ascendentemente según la fecha de vencimiento.
        """
        detalles = []
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return detalles
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE ventas_db")
            sql = """
                SELECT loteID, numeroLote, fechaIngreso, vencimiento, cantidad_ingresada, cantidad_disponible
                FROM lotes_productos
                WHERE prodId = %s
                ORDER BY vencimiento ASC
            """
            cursor.execute(sql, (prodId,))
            detalles = cursor.fetchall()
            cursor.close()
            conexion.close()
        except Error as e:
            print("Error al obtener detalle de lotes:", e)
        return detalles


# Ejemplo de uso:
if __name__ == "__main__":
    gestor = GestorInventario()
    inventario = gestor.obtener_inventario_agrupado()
    print("Inventario agrupado:", inventario)
    
    if inventario:
        prod_id = inventario[0]["prodId"]
        detalle = gestor.obtener_detalle_lotes(prod_id)
        print(f"Detalle de lotes para prodId {prod_id}:", detalle)
