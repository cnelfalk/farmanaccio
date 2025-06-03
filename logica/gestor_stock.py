# src/logica/gestor_stock.py
from tkinter import messagebox
from datos.conexion_bd import ConexionBD
from mysql.connector import Error
from utils.utilidades import Utilidades

class StockManager:
    """
    Clase que maneja la lógica para la gestión de productos.
    
    Provee métodos para:
      - Agregar o actualizar un producto (por nombre, sumando stock y actualizando el precio).
      - Obtener todos los productos.
      - Modificar un producto.
      - Eliminar un producto.
    """
    
    def agregar_o_actualizar_producto(self, producto) -> bool:
        """
        Agrega un nuevo producto o, si ya existe (comparando en minúsculas el nombre),
        actualiza el stock sumando la cantidad y actualiza el precio.
        Retorna True si la operación es exitosa y False en caso contrario.
        """
        # Si la función de validación requiere un parent (para mostrar mensajes), aquí se pasa None.
        if not Utilidades.validar_producto(None, producto):
            return False
        try:
            conexion = ConexionBD.obtener_conexion()
            if not conexion:
                return False
            # Usamos un cursor con dictionary=True para obtener resultados como diccionario.
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE ventas_db")
            sql_busqueda = "SELECT prodId, stock FROM productos WHERE LOWER(nombre) = LOWER(%s)"
            cursor.execute(sql_busqueda, (producto["nombre"],))
            resultado = cursor.fetchone()
            if resultado:
                # Si se encontró el producto, suma el stock existente y actualiza el precio.
                nuevo_stock = resultado["stock"] + producto["stock"]
                sql_update = "UPDATE productos SET stock = %s, precio = %s WHERE prodId = %s"
                cursor.execute(sql_update, (nuevo_stock, producto["precio"], resultado["prodId"]))
            else:
                # Inserta un nuevo producto.
                sql_insert = "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert, (producto["nombre"], producto["precio"], producto["stock"]))
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
        except Error as e:
            messagebox.showerror("Error en agregar o actualizar_producto:", e)
            return False

    def obtener_productos(self) -> list:
        """
        Retorna una lista de todos los productos disponibles en la base de datos.
        """
        productos = []
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("USE ventas_db")
                cursor.execute("SELECT prodId as prodId, nombre, precio, stock FROM productos")
                productos = cursor.fetchall()
                cursor.close()
                conexion.close()
        except Error as e:
            messagebox.showerror("Error al obtener productos:", e)
        return productos

    def modificar_producto(self, parent, id_producto, producto_actualizado) -> bool:
        """
        Modifica los datos de un producto existente.
        Recibe el identificador (id_producto) y un diccionario con los datos actualizados.
        Retorna True si se actualizó con éxito.
        """
        if not Utilidades.validar_producto(parent, producto_actualizado):
            return False
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("USE ventas_db")
                sql = "UPDATE productos SET nombre=%s, precio=%s, stock=%s WHERE prodId=%s"
                datos = (
                    producto_actualizado["nombre"],
                    producto_actualizado["precio"],
                    producto_actualizado["stock"],
                    id_producto
                )
                cursor.execute(sql, datos)
                conexion.commit()
                cursor.close()
                conexion.close()
                return True
        except Error as e:
            messagebox.showerror("Error al modificar producto:", e, parent=parent)
        return False

    def eliminar_producto(self, id_producto) -> bool:
        """
        Elimina el producto que tenga el id indicado.
        Retorna True si la eliminación es exitosa; en caso contrario, False.
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("USE ventas_db")
                sql = "DELETE FROM productos WHERE prodId=%s"
                cursor.execute(sql, (id_producto,))
                conexion.commit()
                cursor.close()
                conexion.close()
                return True
        except Error as e:
            messagebox.showerror("Error al eliminar producto:", e)
        return False

# Ejemplo de uso:
if __name__ == "__main__":
    stock_manager = StockManager()
    
    # Ejemplo: agregar o actualizar un producto.
    producto = {
        "nombre": "Manzana",
        "precio": 1.2,
        "stock": 100
    }
    if stock_manager.agregar_o_actualizar_producto(producto):
        print("Producto agregado/actualizado con éxito.")
    else:
        print("Error al agregar/actualizar el producto.")
    
    # Ejemplo: obtener productos.
    productos = stock_manager.obtener_productos()
    print("Productos:", productos)