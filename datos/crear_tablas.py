# src/crear_tablas.py

from datos.conexion_bd import ConexionBD
from mysql.connector import Error

class TablaCreator:
    """
    Crea la base de datos 'farmanaccio_db' y sus tablas: 
      - vademecum, productos, lotes_productos, usuarios, clientes, facturas, factura_detalles,
      - Remito y RemitoDetalle.
    """
    def crear_base_de_datos_y_tablas(self):
        try:
            conexion = ConexionBD.obtener_conexion()
            if conexion is None:
                raise Exception("No se pudo establecer la conexión con el servidor SQL.")
            cursor = conexion.cursor()
            # Crear la base de datos si no existe
            cursor.execute("CREATE DATABASE IF NOT EXISTS farmanaccio_db")
            cursor.execute("USE farmanaccio_db")

            # Tabla vademecum
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

            # Tabla productos
            sentencia_productos = """
                CREATE TABLE IF NOT EXISTS productos (
                    prodId INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    precio DECIMAL(10,2) NOT NULL,
                    stock INT NOT NULL,
                    activo TINYINT(1) NOT NULL DEFAULT 1
                )
            """
            cursor.execute(sentencia_productos)

            # Tabla lotes_productos
            sentencia_lotes = """
                CREATE TABLE IF NOT EXISTS lotes_productos (
                    loteID INT AUTO_INCREMENT PRIMARY KEY,
                    prodId INT NOT NULL,
                    numeroLote VARCHAR(50) NOT NULL,
                    fechaIngreso DATE NOT NULL,
                    vencimiento DATE NOT NULL,
                    cantidad_ingresada INT NOT NULL,
                    cantidad_disponible INT NOT NULL,
                    UNIQUE(prodId, numeroLote, fechaIngreso),
                    FOREIGN KEY (prodId) REFERENCES productos(prodId)
                )
            """
            cursor.execute(sentencia_lotes)

            # Tabla usuarios
            sentencia_usuarios = """
                CREATE TABLE IF NOT EXISTS usuarios (
                    userId INT AUTO_INCREMENT PRIMARY KEY,
                    usuario VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(100) NOT NULL,
                    role ENUM('admin','empleado') NOT NULL
                )
            """
            cursor.execute(sentencia_usuarios)

            # Tabla clientes  
            # Se modifica para que, en lugar de cuil, se llame `cuil-cuit`
            sentencia_clientes = """
                CREATE TABLE IF NOT EXISTS clientes (
                    clienteId INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    apellido VARCHAR(100) NOT NULL,
                    `cuil-cuit` VARCHAR(20) NOT NULL UNIQUE,
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    direccion VARCHAR(150),
                    iva VARCHAR(50) NOT NULL DEFAULT ''
                )
            """
            cursor.execute(sentencia_clientes)

            # Tabla facturas
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

            # Tabla factura_detalles
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

            # Tablas para Remito y RemitoDetalle
            sentencia_remito = """
                CREATE TABLE IF NOT EXISTS Remito (
                    remitoID INT AUTO_INCREMENT PRIMARY KEY,
                    clienteID INT,
                    cuit_cuil VARCHAR(20),
                    ivaEstado VARCHAR(50),
                    fechaInicio DATE,
                    vencimientoRemito DATE,
                    FOREIGN KEY (clienteID) REFERENCES clientes(clienteId)
                )
            """
            cursor.execute(sentencia_remito)

            sentencia_remito_detalle = """
                CREATE TABLE IF NOT EXISTS RemitoDetalle (
                    remitoDetalleID INT AUTO_INCREMENT PRIMARY KEY,
                    remitoID INT,
                    prodID INT,
                    cantidad INT,
                    FOREIGN KEY (remitoID) REFERENCES Remito(remitoID),
                    FOREIGN KEY (prodID) REFERENCES productos(prodId)
                )
            """
            cursor.execute(sentencia_remito_detalle)

            # Insertar usuario administrador por defecto si no existe.
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
    creador = TablaCreator()
    creador.crear_base_de_datos_y_tablas()
