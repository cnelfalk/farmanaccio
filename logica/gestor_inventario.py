# src/logica/gestor_inventario.py
from datos.conexion_bd import ConexionBD
from mysql.connector import Error

class GestorInventario:
    def _calcular_estado(self, stock: int) -> tuple:
        """
        Calcula el estado del stock.
          - Si stock < 10: retorna ("Crítico", "red")
          - Si 10 ≤ stock < 30: retorna ("Preocupante", "yellow")
          - Si stock ≥ 30: retorna ("Razonable", "green")
        """
        if stock < 10:
            return ("Crítico", "red")
        elif stock < 30:
            return ("Preocupante", "yellow")
        else:
            return ("Razonable", "green")
        
    def obtener_inventario_agrupado(self) -> list:
        """
        Retorna un resumen del inventario agrupado por producto a partir de la tabla lotes_productos,
        para productos activos, y añade dos nuevos campos:
          - total_stock: la suma de las cantidades disponibles (aunque sea 0)
          - vencimiento_proximo: la fecha mínima de vencimiento asociada.
          
        Se eliminó el filtro que restringía a lotes con cantidad_disponible > 0,
        de forma que los productos que hayan agotado todo su stock se muestren con total_stock = 0.
        """
        inventario = []
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return inventario
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE farmanaccio_db")
            sql = """
                SELECT 
                    p.prodId, 
                    p.nombre, 
                    p.precio,
                    IFNULL(SUM(l.cantidad_disponible), 0) AS total_stock,
                    MIN(l.vencimiento) AS vencimiento_proximo
                FROM productos p
                JOIN lotes_productos l ON p.prodId = l.prodId
                WHERE p.activo = 1
                GROUP BY p.prodId, p.nombre, p.precio
            """
            cursor.execute(sql)
            inventario = cursor.fetchall()
            for p in inventario:
                stock = p["total_stock"]
                estado, color = self._calcular_estado(stock)
                p["estado"] = estado
                p["bg_color"] = color
            cursor.close()
            conexion.close()
        except Error as e:
            print("Error al obtener inventario agrupado:", e)
        return inventario

    def obtener_detalles_generales_producto(self, nombre_producto: str) -> dict:
        """
        Retorna un diccionario con los detalles generales del producto a partir del
        vademécum, basado en la columna 'nombreComercial'.
        
        Los detalles incluyen:
          - presentacion
          - accionFarmacologica
          - principioActivo
          - laboratorio
          
        Si no se encuentra el producto, se devuelven valores por defecto.
        """
        detalles = {}
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return {
                    "presentacion": "No Disponible", 
                    "accionFarmacologica": "No Disponible",
                    "principioActivo": "No Disponible", 
                    "laboratorio": "No Disponible"
                }
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE farmanaccio_db")
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
                detalles = {
                    "presentacion": "No Disponible", 
                    "accionFarmacologica": "No Disponible",
                    "principioActivo": "No Disponible", 
                    "laboratorio": "No Disponible"
                }
            cursor.close()
            conexion.close()
        except Exception as e:
            detalles = {
                "presentacion": "No Disponible",
                "accionFarmacologica": "No Disponible",
                "principioActivo": "No Disponible",
                "laboratorio": "No Disponible"
            }
        return detalles

    def obtener_detalle_lotes(self, prodId: int) -> list:
        """
        Retorna la lista de lotes asociados a un producto, ordenados por vencimiento.
        Cada lote se retorna como un diccionario con las columnas:
        loteID, numeroLote, fechaIngreso, vencimiento, cantidad_ingresada y cantidad_disponible.
        """
        detalles = []
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return detalles
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE farmanaccio_db")
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
        # Suponiendo que el nombre del producto corresponde al 'nombreComercial'
        detalles_generales = gestor.obtener_detalles_generales_producto(inventario[0]["nombre"])
        print("Detalles generales del producto:", detalles_generales)
        detalle_lotes = gestor.obtener_detalle_lotes(prod_id)
        print(f"Detalle de lotes para prodId {prod_id}:", detalle_lotes)
