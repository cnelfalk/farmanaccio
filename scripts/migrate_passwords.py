# scripts/migrate_passwords.py
from datos.conexion_bd import ConexionBD
from utils.security import hash_password, is_hashed

def migrar_passwords():
    cnx = ConexionBD.obtener_conexion()
    cur = cnx.cursor()
    cur.execute("USE farmanaccio_db")

    cur.execute("SELECT userID, password FROM usuarios")
    for userID, pwd in cur.fetchall():
        # solo hash si NO es ya un hash válido
        if not is_hashed(pwd):
            nuevo = hash_password(pwd)
            cur.execute(
                "UPDATE usuarios SET password=%s WHERE userID=%s",
                (nuevo, userID)
            )

    cnx.commit()
    cur.close()
    cnx.close()
