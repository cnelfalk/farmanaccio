# src/logica/gestor_clientes.py
from datos.conexion_bd import ConexionBD
from mysql.connector import Error
import tkinter.messagebox as messagebox
from tkinter import simpledialog

class ClienteManager:
    """
    CRUD clientes + archivado con razón (campo 'razonArchivado').
    """

    def crear_cliente(self, cliente: dict) -> bool:
        try:
            cnx = ConexionBD.obtener_conexion()
            if cnx is None: return False
            cur = cnx.cursor()
            cur.execute("USE farmanaccio_db")
            sql = """
              INSERT INTO clientes
                (nombre,apellido,`cuil-cuit`,telefono,email,direccion,iva)
              VALUES(%s,%s,%s,%s,%s,%s,%s)
            """
            datos = (
                cliente["nombre"], cliente["apellido"],
                cliente["cuil"], cliente.get("telefono",""),
                cliente.get("email",""), cliente.get("direccion",""),
                cliente.get("iva","")
            )
            cur.execute(sql,datos)
            cnx.commit()
            cur.close(); cnx.close()
            return True
        except Error as e:
            messagebox.showerror("Error al crear cliente",str(e))
            return False

    def obtener_clientes(self) -> list:
        try:
            cnx = ConexionBD.obtener_conexion()
            if cnx is None: return []
            cur = cnx.cursor(dictionary=True)
            cur.execute("USE farmanaccio_db")
            # Incluimos razonArchivado en la consulta
            cur.execute("""
              SELECT clienteID,
                     nombre,
                     apellido,
                     `cuil-cuit` AS cuil,
                     telefono,
                     email,
                     direccion,
                     iva,
                     activo,
                     razonArchivado
                FROM clientes
            """)
            rows = cur.fetchall()
            cur.close()
            cnx.close()
            return rows
        except Error as e:
            messagebox.showerror("Error al obtener clientes", str(e))
            return []


    def actualizar_cliente(self, cid:int, cliente:dict) -> bool:
        try:
            cnx = ConexionBD.obtener_conexion()
            if cnx is None: return False
            cur = cnx.cursor()
            cur.execute("USE farmanaccio_db")
            sql = """
              UPDATE clientes SET
                nombre=%s,apellido=%s,`cuil-cuit`=%s,
                telefono=%s,email=%s,direccion=%s,iva=%s
              WHERE clienteID=%s
            """
            datos=(
                cliente["nombre"],cliente["apellido"],cliente["cuil"],
                cliente.get("telefono",""),cliente.get("email",""),
                cliente.get("direccion",""),cliente.get("iva",""),
                cid
            )
            cur.execute(sql,datos)
            cnx.commit()
            cur.close(); cnx.close()
            return True
        except Error as e:
            messagebox.showerror("Error al actualizar cliente",str(e))
            return False

    def eliminar_cliente(self, cid: int, razon: str) -> bool:
        try:
            cnx = ConexionBD.obtener_conexion()
            if cnx is None:
                return False
            cur = cnx.cursor()
            cur.execute("USE farmanaccio_db")
            cur.execute("""
                UPDATE clientes
                SET activo = 0,
                    razonArchivado = %s
                WHERE clienteID = %s
            """, (razon, cid))
            cnx.commit()
            cur.close(); cnx.close()
            return True
        except Error as e:
            messagebox.showerror("Error al archivar cliente", str(e))
            return False
    
    def restaurar_cliente(self, cliente_id: int) -> bool:
        try:
            cnx = ConexionBD.obtener_conexion()
            cur = cnx.cursor()
            cur.execute("USE farmanaccio_db")
            cur.execute("UPDATE clientes SET activo = 1 WHERE clienteID = %s", (cliente_id,))
            cnx.commit()
            cur.close(); cnx.close()
            return True
        except Error as e:
            messagebox.showerror("Error al restaurar cliente", str(e))
            return False
