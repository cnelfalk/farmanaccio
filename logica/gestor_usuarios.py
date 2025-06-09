# src/logica/gestor_usuarios.py
from datos.conexion_bd import ConexionBD
from mysql.connector import Error

class UsuarioManager:
    """
    Clase encargada de gestionar las operaciones relacionadas con los usuarios
    en la base de datos (farmanaccio_db). Incluye métodos para:
      - Validar credenciales.
      - Crear un nuevo usuario.
      - Obtener todos los usuarios.
      - Eliminar un usuario.
      - Actualizar los datos de un usuario.
    """

    def validar_usuario(self, usuario: str, password: str):
        """
        Busca en la tabla 'usuarios' un registro que coincida con el usuario y
        la contraseña. Retorna un diccionario con la información si las credenciales
        son correctas, o None en caso contrario.
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return None

            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE farmanaccio_db")
            cursor.execute(
                "SELECT userId, usuario, password, role FROM usuarios WHERE usuario = %s",
                (usuario,)
            )
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()

            if resultado and resultado["password"] == password:
                return resultado
            return None
        except Error as e:
            print("Error al validar usuario:", e)
            return None

    def crear_usuario(self, usuario: str, password: str, rol: str) -> bool:
        """
        Inserta un nuevo usuario en la base de datos. Retorna True si se creó correctamente,
        o False en caso de error.
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return False

            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            cursor.execute(
                "INSERT INTO usuarios (usuario, password, role) VALUES (%s, %s, %s)",
                (usuario, password, rol)
            )
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
        except Error as e:
            print("Error al crear usuario:", e)
            return False

    def obtener_usuarios(self) -> list:
        """
        Retorna una lista con la información de todos los usuarios existentes en la base de datos.
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            cursor.execute("SELECT userId, usuario, password, role FROM usuarios")
            usuarios = cursor.fetchall()
            conexion.close()
            return usuarios
        except Error as e:
            print("Error al obtener usuarios:", e)
            return []

    def eliminar_usuario(self, id_usuario) -> bool:
        """
        Elimina el usuario cuyo identificador sea igual a 'id_usuario'.
        Retorna True si se eliminó correctamente o False en caso de error.
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            cursor.execute("DELETE FROM usuarios WHERE userId = %s", (id_usuario,))
            conexion.commit()
            return cursor.rowcount > 0
        except Error:
            return False
        finally:
            conexion.close()

    def actualizar_usuario(self, id_usuario, usuario: str, password: str, rol: str) -> bool:
        """
        Actualiza los datos del usuario identificado por 'id_usuario'. Retorna True si se actualizó con éxito,
        o False en caso contrario.
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            cursor.execute(
                """
                UPDATE usuarios 
                SET usuario = %s, password = %s, role = %s 
                WHERE userId = %s
                """,
                (usuario, password, rol, id_usuario)
            )
            conexion.commit()
            return cursor.rowcount > 0
        except Error:
            return False
        finally:
            conexion.close()

# Ejemplo de uso:
if __name__ == "__main__":
    um = UsuarioManager()
    
    # Validar credenciales (por ejemplo, usuario "admin" con contraseña "admin")
    user = um.validar_usuario("admin", "admin")
    if user:
        print("Usuario validado:", user)
    else:
        print("Credenciales incorrectas")
    
    # Crear un nuevo usuario:
    if um.crear_usuario("nuevo_usuario", "pass123", "empleado"):
        print("Usuario creado exitosamente.")
    else:
        print("Error al crear usuario.")
    
    # Obtener la lista de usuarios
    usuarios = um.obtener_usuarios()
    print("Usuarios:", usuarios)