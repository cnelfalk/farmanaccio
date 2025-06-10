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
      - Obtener usuarios por estado (activo/inactivo).
      - "Eliminar" un usuario (actualizando el campo 'activo' a 0).
      - Restaurar un usuario (estableciendo 'activo' a 1).
      - Actualizar datos de un usuario.
    """

    def validar_usuario(self, usuario: str, password: str):
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return None
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE farmanaccio_db")
            cursor.execute(
                "SELECT userId, usuario, password, role, activo FROM usuarios WHERE usuario = %s",
                (usuario,)
            )
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()
            if resultado:
                if resultado["password"] == password:
                    if resultado.get("activo", 0) != 1:
                        return "inactivo"
                    return resultado
            return None
        except Error as e:
            print("Error al validar usuario:", e)
            return None

    def crear_usuario(self, usuario: str, password: str, rol: str) -> bool:
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return False
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            cursor.execute("INSERT INTO usuarios (usuario, password, role) VALUES (%s, %s, %s)",
                           (usuario, password, rol))
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
        except Error as e:
            print("Error al crear usuario:", e)
            return False

    def obtener_usuarios(self) -> list:
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE farmanaccio_db")
            cursor.execute("SELECT userId, usuario, password, role, activo FROM usuarios")
            usuarios = cursor.fetchall()
            cursor.close()
            conexion.close()
            return usuarios
        except Error as e:
            print("Error al obtener usuarios:", e)
            return []

    def obtener_usuarios_por_estado(self, activo: int) -> list:
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE farmanaccio_db")
            cursor.execute("SELECT userId, usuario, password, role, activo FROM usuarios WHERE activo = %s", (activo,))
            usuarios = cursor.fetchall()
            cursor.close()
            conexion.close()
            return usuarios
        except Error as e:
            print("Error al obtener usuarios por estado:", e)
            return []

    def eliminar_usuario(self, id_usuario) -> bool:
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            cursor.execute("UPDATE usuarios SET activo = 0 WHERE userId = %s", (id_usuario,))
            conexion.commit()
            affected = cursor.rowcount
            cursor.close()
            conexion.close()
            return affected > 0
        except Error as e:
            print("Error al eliminar usuario:", e)
            return False

    def restaurar_usuario(self, id_usuario, nuevo_rol) -> bool:
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                return False
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            # Actualizamos activo a 1 y asignamos el rol recibido
            cursor.execute("UPDATE usuarios SET activo = 1, role = %s WHERE userId = %s", (nuevo_rol, id_usuario))
            conexion.commit()
            affected = cursor.rowcount
            cursor.close()
            conexion.close()
            return affected > 0
        except Error as e:
            print("Error al restaurar usuario:", e)
            return False

    def actualizar_usuario(self, id_usuario, usuario: str, password: str, rol: str) -> bool:
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("USE farmanaccio_db")
            cursor.execute(
                "UPDATE usuarios SET usuario = %s, password = %s, role = %s WHERE userId = %s",
                (usuario, password, rol, id_usuario)
            )
            conexion.commit()
            affected = cursor.rowcount
            cursor.close()
            conexion.close()
            return affected > 0
        except Error as e:
            print("Error al actualizar usuario:", e)
            return False

if __name__ == "__main__":
    um = UsuarioManager()
    user = um.validar_usuario("admin", "admin")
    print("Usuario validado:", user)

    if um.crear_usuario("nuevo_usuario", "pass123", "empleado"):
        print("Usuario creado exitosamente.")
    else:
        print("Error al crear usuario.")

    print("Todos los usuarios:")
    print(um.obtener_usuarios())
    print("Usuarios activos:")
    print(um.obtener_usuarios_por_estado(1))
    print("Usuarios inactivos:")
    print(um.obtener_usuarios_por_estado(0))
