# src/datos/crear_tablas.py

import os
import pandas as pd
from datos.conexion_bd import ConexionBD
from mysql.connector import Error

class TablaCreator:
    """
    Crea la base de datos 'farmanaccio_db' y sus tablas:
      - vademecum, productos, lotes_productos, usuarios, clientes,
        facturas, factura_detalles, Remito (con clienteDireccion) y RemitoDetalle.
    Además inserta datos iniciales.
    """

    def crear_base_de_datos_y_tablas(self):
        try:
            # 1) Conexión y creación de la base
            cnx = ConexionBD.obtener_conexion()
            if cnx is None:
                raise Exception("No se pudo conectar a MySQL.")
            cursor = cnx.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS farmanaccio_db")
            cursor.execute("USE farmanaccio_db")

            # 2) Definición de tablas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                  userID INT AUTO_INCREMENT PRIMARY KEY,
                  usuario VARCHAR(50) NOT NULL UNIQUE,
                  password VARCHAR(100) NOT NULL,
                  role ENUM('admin','empleado') NOT NULL,
                  activo TINYINT(1) NOT NULL DEFAULT 1,
                  razonArchivado VARCHAR(300) NOT NULL DEFAULT ''
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                  clienteID INT AUTO_INCREMENT PRIMARY KEY,
                  nombre VARCHAR(100) NOT NULL,
                  apellido VARCHAR(100) NOT NULL,
                  `cuil-cuit` VARCHAR(20) NOT NULL UNIQUE,
                  telefono VARCHAR(20),
                  email VARCHAR(100),
                  direccion VARCHAR(150),
                  iva VARCHAR(50) NOT NULL DEFAULT '',
                  activo TINYINT(1) NOT NULL DEFAULT 1,
                  razonArchivado VARCHAR(300) NOT NULL DEFAULT ''
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vademecum (
                  vademecumID INT AUTO_INCREMENT PRIMARY KEY,
                  nombreComercial VARCHAR(255) NOT NULL,
                  presentacion VARCHAR(255) NOT NULL,
                  accionFarmacologica VARCHAR(255) NOT NULL,
                  principioActivo VARCHAR(255) NOT NULL,
                  laboratorio VARCHAR(255) NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                  prodID INT AUTO_INCREMENT PRIMARY KEY,
                  nombre VARCHAR(100) NOT NULL,
                  precio DECIMAL(10,2) NOT NULL,
                  stock INT NOT NULL,
                  activo TINYINT(1) NOT NULL DEFAULT 1,
                  razonArchivado VARCHAR(300) NOT NULL DEFAULT ''
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lotes_productos (
                  loteID INT AUTO_INCREMENT PRIMARY KEY,
                  prodID INT NOT NULL,
                  numeroLote VARCHAR(50) NOT NULL,
                  fechaIngreso DATE NOT NULL,
                  vencimiento DATE NOT NULL,
                  cantidad_ingresada INT NOT NULL,
                  cantidad_disponible INT NOT NULL,
                  UNIQUE(prodID, numeroLote, fechaIngreso),
                  FOREIGN KEY (prodID) REFERENCES productos(prodID)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS facturas (
                  facturaID   INT AUTO_INCREMENT PRIMARY KEY,
                  clienteID   INT NULL,
                  fechaEmision DATE    DEFAULT CURRENT_DATE,
                  horaEmision  TIME,
                  total_neto   DECIMAL(10,2) NOT NULL,
                  total_bruto  DECIMAL(10,2) NOT NULL,
                  descuento    DECIMAL(5,2) DEFAULT 0.00,
                  tipoFactura  ENUM('A','B','C') NOT NULL DEFAULT 'B',
                  FOREIGN KEY (clienteID) REFERENCES clientes(clienteID)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS factura_detalles (
                  facturaDetalleID INT AUTO_INCREMENT PRIMARY KEY,
                  facturaID INT,
                  prodID INT,
                  cantidad INT,
                  precioUnitario DECIMAL(10,2) NOT NULL,
                  FOREIGN KEY (facturaID) REFERENCES facturas(facturaID)
                )
            """)
            # Aquí agregamos clienteDireccion
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Remito (
                  remitoID INT AUTO_INCREMENT PRIMARY KEY,
                  clienteID INT,
                  cuit_cuil VARCHAR(20),
                  ivaEstado VARCHAR(50),
                  direccionCliente VARCHAR(150),
                  fechaInicio DATE,
                  vencimientoRemito DATE,
                  FOREIGN KEY (clienteID) REFERENCES clientes(clienteID)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS RemitoDetalle (
                  remitoDetalleID INT AUTO_INCREMENT PRIMARY KEY,
                  remitoID INT,
                  prodID INT,
                  cantidad INT,
                  FOREIGN KEY (remitoID) REFERENCES Remito(remitoID),
                  FOREIGN KEY (prodID)    REFERENCES productos(prodID)
                )
            """)

            # 3) Inserción de datos iniciales
            usuarios_default = [
                ('admin',      'admin',    'admin'),
                ('empleado1', 'pass1',    'empleado'),
                ('empleado2', 'pass2',    'empleado')
            ]
            for u, pw, rl in usuarios_default:
                cursor.execute(
                    "INSERT IGNORE INTO usuarios(usuario,password,role) VALUES(%s,%s,%s)",
                    (u, pw, rl)
                )

            clientes_default = [
                ('Carlos', 'López',    '20-11111111-1', '555-1001', 'carlos.lopez@ej.com', 'Calle Alfa 1',    'Exento'),
                ('María',  'González', '20-22222222-2', '555-1002', 'maria.gonzalez@ej.com', 'Calle Beta 2',    'Monotributo'),
                ('Pedro',  'Fernández','20-33333333-3', '555-1003', 'pedro.fernandez@ej.com', 'Calle Gamma 3',   'Resp. Insc.'),
                ('Lucía',  'Martínez', '20-44444444-4', '555-1004', 'lucia.martinez@ej.com',  'Calle Delta 4',   'Eventual'),
                ('José',   'Ramírez',  '20-55555555-5', '555-1005', 'jose.ramirez@ej.com',    'Calle Épsilon 5', 'Cons. Final')
            ]
            for n, a, c, t, e, d, iva in clientes_default:
                cursor.execute(
                    """INSERT IGNORE INTO clientes
                       (nombre,apellido,`cuil-cuit`,telefono,email,direccion,iva)
                       VALUES(%s,%s,%s,%s,%s,%s,%s)""",
                    (n, a, c, t, e, d, iva)
                )

            cursor.execute("SELECT COUNT(*) FROM productos")
            total_prod = cursor.fetchone()[0]
            if total_prod == 0:
                ruta_excel = os.path.join(os.path.dirname(__file__), "vademecum-marzo2025.xlsx")
                df = pd.read_excel(ruta_excel, sheet_name=0)
                nombres = (
                    df["nombre-comercial"]
                    .dropna().astype(str)
                    .str.strip().drop_duplicates()
                    .tolist()
                )[:5]
                precios_default = [1000.00, 1200.50, 800.75, 1500.00, 5000.00]
                for nombre_com, precio in zip(nombres, precios_default):
                    cursor.execute(
                        "INSERT INTO productos(nombre,precio,stock,activo) VALUES(%s,%s,%s,1)",
                        (nombre_com, precio, 20)
                    )
                    cursor.execute(
                        "SELECT prodID FROM productos WHERE nombre=%s LIMIT 1",
                        (nombre_com,)
                    )
                    row = cursor.fetchone()
                    if not row:
                        continue
                    prod_id = row[0]
                    cursor.execute(
                        """INSERT INTO lotes_productos
                           (prodID, numeroLote, fechaIngreso, vencimiento, cantidad_ingresada, cantidad_disponible)
                           VALUES(%s,'INI',CURDATE(),
                                  DATE_ADD(CURDATE(), INTERVAL 1 YEAR),
                                  20,20)""",
                        (prod_id,)
                    )

            # 4) Commit y cierre
            cnx.commit()
            cursor.close()
            cnx.close()
            print("Base de datos, tablas y datos iniciales creados con éxito.")

        except Error as sql_e:
            print("Error durante creación de tablas o inserción de datos:", sql_e)
        except Exception as e:
            print("Error general en crear_tablas:", e)


if __name__ == "__main__":
    TablaCreator().crear_base_de_datos_y_tablas()
