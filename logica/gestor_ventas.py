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
        Confirma una venta actualizando el stock y
        creando un registro en las tablas 'facturas' y 'factura_detalles'.
        Retorna (bool, str) según corresponda.
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return False, "No se pudo conectar a la base de datos."
            
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE ventas_db")
            
            total_bruto = 0.0
            # Verifica el stock y calcula el total
            for item in carrito:
                id_producto = item['prodId']
                cantidad_vendida = item['cantidad']
                
                cursor.execute("SELECT stock, precio FROM productos WHERE prodId=%s", (id_producto,))
                resultado = cursor.fetchone()
                if resultado is None:
                    conexion.rollback()
                    return False, f"Producto con ID {id_producto} no encontrado."
                
                stock_actual = resultado['stock']
                precio_unitario = resultado['precio']
                if stock_actual < cantidad_vendida:
                    conexion.rollback()
                    return False, f"Stock insuficiente para el producto ID {id_producto}."
                
                total_bruto += float(precio_unitario) * cantidad_vendida
            
            # Puedes calcular un descuento si lo manejas (ejemplo: descuento del 0% si no hay descuento)
            descuento = 0.0  
            total_neto = total_bruto * (1 - descuento / 100)
            
            # Inserta la factura en la tabla 'facturas'
            cursor.execute(
                """
                INSERT INTO facturas (fechaEmision, horaEmision, total_neto, total_bruto, descuento)
                VALUES (CURRENT_DATE, CURRENT_TIME, %s, %s, %s)
                """,
                (total_neto, total_bruto, descuento)
            )
            factura_id = cursor.lastrowid  # Obtén el ID de la factura recién insertada
            
            # Inserta cada detalle en la tabla 'factura_detalles'
            for item in carrito:
                cursor.execute("SELECT precio FROM productos WHERE prodId=%s", (item['prodId'],))
                precio_unitario = cursor.fetchone()['precio']
                cursor.execute(
                    """
                    INSERT INTO factura_detalles (facturaId, prodId, cantidad, precioUnitario)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (factura_id, item['prodId'], item['cantidad'], precio_unitario)
                )
                # Actualiza el stock del producto
                cursor.execute("SELECT stock FROM productos WHERE prodId=%s", (item['prodId'],))
                nuevo_stock = cursor.fetchone()['stock'] - item['cantidad']
                cursor.execute("UPDATE productos SET stock=%s WHERE prodId=%s", (nuevo_stock, item['prodId']))
            
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