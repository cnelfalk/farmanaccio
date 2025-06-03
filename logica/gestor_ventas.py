# src/logica/gestor_ventas.py
from datos.conexion_bd import ConexionBD
from mysql.connector import Error

class VentaManager:
    """
    Clase para gestionar la confirmación de ventas.
    
    El método 'confirmar_venta' verifica el stock de cada producto del carrito, 
    actualiza la base de datos en consecuencia y devuelve un mensaje indicativo del resultado.
    """

    def confirmar_venta(self, carrito):
        """
        Confirma una venta actualizando el stock de productos según la cantidad vendida.
        
        Parámetros:
            carrito: Lista de diccionarios, donde cada diccionario debe contener:
                     - 'prodId': ID del producto.
                     - 'cantidad': Cantidad vendida.
        
        Retorna:
            Una tupla (bool, str) en la que:
              - El primer elemento indica si la venta fue confirmada exitosamente.
              - El segundo elemento es un mensaje que explica el resultado.
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return False, "No se pudo conectar a la base de datos."
            
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE ventas_db")
            
            for item in carrito:
                id_producto = item['prodId']
                cantidad_vendida = item['cantidad']
                
                # Verificar el stock disponible del producto
                cursor.execute("SELECT stock FROM productos WHERE prodId=%s", (id_producto,))
                resultado = cursor.fetchone()
                if resultado is None:
                    conexion.rollback()
                    return False, f"Producto con ID {id_producto} no encontrado."
                
                stock_actual = resultado['stock']
                if stock_actual < cantidad_vendida:
                    conexion.rollback()
                    return False, f"Stock insuficiente para el producto ID {id_producto}."
                
                nuevo_stock = stock_actual - cantidad_vendida
                cursor.execute("UPDATE productos SET stock=%s WHERE prodId=%s", (nuevo_stock, id_producto))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Venta confirmada exitosamente. Proceda a elegir dónde guardará la factura."
        except Error as e:
            return False, str(e)

# Ejemplo de uso:
if __name__ == "__main__":
    venta_manager = VentaManager()
    carrito_ejemplo = [
        {'prodId': 1, 'cantidad': 2},
        {'prodId': 3, 'cantidad': 1}
    ]
    resultado, mensaje = venta_manager.confirmar_venta(carrito_ejemplo)
    print("Resultado:", resultado, "Mensaje:", mensaje)