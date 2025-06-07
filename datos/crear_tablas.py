# src/datos/crear_tablas.py
from datos.conexion_bd import ConexionBD
from mysql.connector import Error

class TablaCreator:
    """
    Clase encargada de crear la base de datos 'ventas_db' y sus tablas asociadas.
    Esto incluye:
      - La creación de la base de datos (si no existe)
      - Tablas: productos, usuarios, clientes, facturas, factura_detalles y vademecum.
      - Inserción de un usuario administrador por defecto (si no existe)
    """
    
    def crear_base_de_datos_y_tablas(self):
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                raise Exception("No se pudo establecer la conexión con el servidor SQL.")
            
            cursor = conexion.cursor()
            
            # Crear la base de datos si no existe
            cursor.execute("CREATE DATABASE IF NOT EXISTS ventas_db")
            cursor.execute("USE ventas_db")

            # Crear la tabla vademecum, según los atributos especificados
            sentencia_vademecum = """
                CREATE TABLE IF NOT EXISTS vademecum (
                    vademecumID INT AUTO_INCREMENT PRIMARY KEY,
                    nombreComercial VARCHAR(255) NOT NULL,
                    presentacion VARCHAR(255) NOT NULL,
                    accionFarmacologica VARCHAR(255) NOT NULL,
                    principioActivo VARCHAR(255) NOT NULL,
                    laboratorio VARCHAR(255) NOT NULL
                )
            """
            cursor.execute(sentencia_vademecum)
            
            # Crear la tabla de productos
            sentencia_productos = """
                CREATE TABLE IF NOT EXISTS productos (
                    prodId INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    precio DECIMAL(10,2) NOT NULL,
                    stock INT NOT NULL
                )
            """
            cursor.execute(sentencia_productos)

            sentencia_detalletrazabilidad = """
                CREATE TABLE IF NOT EXISTS detalleTrazabilidad (
                    prodId
                    
                    )

            """
            
            # Crear la tabla de usuarios
            sentencia_usuarios = """
                CREATE TABLE IF NOT EXISTS usuarios (
                    userId INT AUTO_INCREMENT PRIMARY KEY,
                    usuario VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(100) NOT NULL,
                    role ENUM('admin','empleado') NOT NULL
                )
            """
            cursor.execute(sentencia_usuarios)
            
            # Crear la tabla de clientes
            sentencia_clientes = """
                CREATE TABLE IF NOT EXISTS clientes (
                    clienteId INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    apellido VARCHAR(100) NOT NULL,
                    cuil VARCHAR(20) NOT NULL UNIQUE,
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    direccion VARCHAR(150)
                )
            """
            cursor.execute(sentencia_clientes)
            
            # Crear la tabla de facturas
            sentencia_facturas = """
                CREATE TABLE IF NOT EXISTS facturas (
                    facturaId INT AUTO_INCREMENT PRIMARY KEY,
                    fechaEmision DATE DEFAULT CURRENT_DATE,
                    horaEmision TIME,
                    total_neto DECIMAL(10, 2) NOT NULL,
                    total_bruto DECIMAL(10, 2) NOT NULL,
                    descuento DECIMAL(5, 2) DEFAULT 0.00
                )
            """
            cursor.execute(sentencia_facturas)
            
            # Crear la tabla de factura_detalles
            sentencia_factura_detalles = """
                CREATE TABLE IF NOT EXISTS factura_detalles (
                    facturaDetalleId INT AUTO_INCREMENT PRIMARY KEY,
                    facturaId INT,
                    prodId INT,
                    cantidad INT,
                    precioUnitario DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (facturaId) REFERENCES facturas(facturaId)
                )
            """
            cursor.execute(sentencia_factura_detalles)
            
            # Insertar un usuario administrador por defecto si no existe
            cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO usuarios (usuario, password, role) VALUES ('admin', 'admin', 'admin')")
            
            conexion.commit()
            cursor.close()
            conexion.close()
            print("Base de datos y tablas creadas exitosamente.")
        except Error as e:
            print("Error durante la creación de la base de datos y tablas:", e)
        except Exception as ex:
            print("Error:", ex)

if __name__ == "__main__":
    # Si el script se ejecuta directamente, se crea la base de datos y las tablas.
    creador = TablaCreator()
    creador.crear_base_de_datos_y_tablas()
