# src/logica/gestor_clientes.py
from datos.conexion_bd import ConexionBD
from mysql.connector import Error
import tkinter.messagebox as messagebox

class ClienteManager:
    """
    Clase para gestionar operaciones CRUD sobre clientes en la base de datos.

    Provee métodos para crear, obtener, actualizar y eliminar clientes.
    """

    def crear_cliente(self, cliente: dict) -> bool:
        """
        Inserta un nuevo cliente en la base de datos.
        
        El diccionario 'cliente' debe contener las claves:
          - 'nombre'
          - 'apellido'
          - 'cuil'
          - 'telefono' (opcional)
          - 'email' (opcional)
          - 'direccion' (opcional)
          - 'iva' (opcional; en caso de no completarse, se almacena vacío)
        
        Retorna True si la operación es exitosa, o False en caso contrario.
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return False
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            sql = """
                INSERT INTO clientes (nombre, apellido, `cuil-cuit`, telefono, email, direccion, iva)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            datos = (
                cliente["nombre"],
                cliente["apellido"],
                cliente["cuil"],
                cliente.get("telefono", ""),
                cliente.get("email", ""),
                cliente.get("direccion", ""),
                cliente.get("iva", "")
            )
            cursor.execute(sql, datos)
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
        except Error as e:
            messagebox.showerror("Error al crear cliente", str(e))
            return False

    def obtener_clientes(self) -> list:
        """
        Retorna una lista con todos los clientes registrados en la base de datos.
        Cada cliente se retorna como un diccionario, incluyendo el campo 'iva'.
        Se utiliza un alias (`AS cuil`) para extraer la columna `cuil-cuit`
        y trabajar con ella de forma uniforme en el código.
        """
        clientes = []
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return clientes
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE farmanaccio_db")
            cursor.execute(
                "SELECT clienteId, nombre, apellido, `cuil-cuit` AS cuil, telefono, email, direccion, iva FROM clientes"
            )
            clientes = cursor.fetchall()
            cursor.close()
            conexion.close()
        except Error as e:
            messagebox.showerror("Error al obtener clientes", str(e))
        return clientes

    def actualizar_cliente(self, clienteId: int, cliente: dict) -> bool:
        """
        Actualiza los datos del cliente identificado por 'clienteId' con la información proveída en 'cliente'.
        Se actualizan los campos: nombre, apellido, cuil, telefono, email, direccion y iva.
        La columna de cuil se actualiza usando el nombre real en la BD (`cuil-cuit`).
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return False
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            sql = """
                UPDATE clientes
                SET nombre = %s, apellido = %s, `cuil-cuit` = %s, telefono = %s, email = %s, direccion = %s, iva = %s
                WHERE clienteId = %s
            """
            datos = (
                cliente["nombre"],
                cliente["apellido"],
                cliente["cuil"],
                cliente.get("telefono", ""),
                cliente.get("email", ""),
                cliente.get("direccion", ""),
                cliente.get("iva", ""),
                clienteId
            )
            cursor.execute(sql, datos)
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
        except Error as e:
            messagebox.showerror("Error al actualizar cliente", str(e))
            return False

    def eliminar_cliente(self, clienteId: int) -> bool:
        """
        Elimina el cliente con el identificador 'clienteId' de la base de datos.
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return False
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            sql = "DELETE FROM clientes WHERE clienteId = %s"
            cursor.execute(sql, (clienteId,))
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
        except Error as e:
            messagebox.showerror("Error al eliminar cliente", str(e))
            return False

if __name__ == "__main__":
    # Ejemplo de uso:
    cm = ClienteManager()

    # Crear un cliente de ejemplo
    cliente_ejemplo = {
        "nombre": "Ana",
        "apellido": "González",
        "cuil": "20-87654321-9",
        "telefono": "555-6789",
        "email": "ana@example.com",
        "direccion": "Av. Siempre Viva 742",
        "iva": "Monotributo"  # Este valor se puede dejar vacío o definirse según el caso
    }
    if cm.crear_cliente(cliente_ejemplo):
        print("Cliente creado exitosamente.")

    # Mostrar todos los clientes
    clientes = cm.obtener_clientes()
    print("Clientes registrados:", clientes)
