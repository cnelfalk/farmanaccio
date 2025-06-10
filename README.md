<p align="center">
  <img src="https://github.com/user-attachments/assets/b03bca29-a15a-48b0-bd9f-8574b5d9da7c" alt="FarmaNaccio (Logotipo)">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python%20-%203.13%20-%20%23FFC92B" alt="Python">
  <img src="https://img.shields.io/badge/UI%20-%20CustomTkinter%20-%20%23446DFF" alt="CustomTkinter">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL">
</p>

## Dependencias externas
* [mysql-connector-python](https://pypi.org/project/mysql-connector-python/)
* [customtkinter](https://pypi.org/project/customtkinter/)
* [CTkMessagebox](https://pypi.org/project/CTkMessagebox/)
* [Pillow](https://pypi.org/project/pillow/)
* [docxtpl](https://pypi.org/project/docxtpl/)
* [docx2pdf](https://pypi.org/project/docx2pdf/)
* [python-docx](https://pypi.org/project/python-docx/)

## Síntesis
Sistema informático programado en Python para utilizarse en el contexto de una farmacia.  
FarmaNaccio integra gestión de usuarios, clientes, stock e inventario, y ventas, con una interfaz moderna desarrollada con CustomTkinter.

Este proyecto se ha realizado aplicando la metodología ágil "Programación Extrema" (XP) utilizando [Trello](https://trello.com/).

## Participantes
- **Alumnos (Programadores):**
  - Matías Daniel Chiacchio
  - Luis Ariel Espinoza
  - Fabrizio Manuel Mansilla

- **Profesores:**
  - Cristian Fernando Cerquand
  - Johanna Motta

# Manual de Usuario

## 1. Inicio Rápido

1. **Inicie XAMPP:**  
   Antes de ejecutar el programa, abra XAMPP (o asegúrese de que el servicio MySQL esté activo).

2. **Ejecute la Aplicación:**  
   Ejecute `principal.py` desde el directorio raíz del proyecto.  
   En la primera ejecución, se crean la base de datos y las tablas necesarias, y se realiza la migración del vademécum.

---

## 2. Pantalla de Login

La **Pantalla de Login** es la puerta de entrada a FarmaNaccio:

- **Campos de Usuario y Contraseña:**  
  Ingrese sus credenciales. Si se dejan campos vacíos, aparecerá una advertencia.
  
- **Botón "Ingresar":**  
  Valida las credenciales consultando la base de datos.

- **Botón de Salida ("×"):**  
  Ubicado en la esquina superior (ahora posicionado en la parte superior derecha conforme a los ajustes de estilo), permite cerrar la aplicación.

---

## 3. Ventana Principal

Tras un inicio de sesión exitoso se desplegará la **Ventana Principal**, la cual centraliza el acceso a los módulos del sistema:

- **Menú de Usuario:**  
  - Muestra el usuario activo.
  - Al hacer clic se despliega un menú con las opciones de agregar/administrar usuarios y cerrar sesión.  
  - El módulo de administración permite filtrar entre usuarios activos/inactivos y actualizar el rol al restaurar usuarios inactivos.

- **Acceso a Módulos:**  
  En el área central se encuentran botones para:
  - **Control de Stock**
  - **Gestión de Ventas**
  - **Gestión de Clientes**

---

## 4. Gestión de Usuarios

Permite administrar los usuarios del sistema:

### Agregar Usuario

- Seleccione **"(+) Agregar usuario"** desde el menú.
- Complete el formulario (Nombre de Usuario, Contraseña –con opción de mostrar/ocultar– y Rol).
- Pulse **"Guardar"**.  
  Se valida que la contraseña tenga al menos 5 caracteres y que los campos obligatorios estén completos.

### Administrar Usuarios

- Seleccione **"Administrar usuarios"** para ver la lista de usuarios en una tabla.
- Funciones adicionales:
  - **Filtrado por Estado:** permite cambiar entre usuarios activos e inactivos.
  - **Modificar y Eliminar:** Realice cambios en usuarios activos.
  - **Restaurar Usuario:** Desde el listado de usuarios inactivos se puede restaurar a un usuario, actualizando también el rol según lo seleccionado en el combobox.

---

## 5. Gestión de Clientes

El módulo de clientes permite gestionar los datos de sus clientes.

### Registro y Consulta

- Acceda a través del botón **"Gestión de Clientes"**.
- La pantalla muestra:
  - Un campo de búsqueda para filtrar clientes por **Nombre, Apellido o CUIL**.
  - Una tabla con clientes registrados (ID, Nombre, Apellido, CUIL, Teléfono, Email y Dirección).

### Edición y Eliminación

- Seleccione un cliente para cargar sus datos.
- Use las opciones **Modificar** o **Eliminar** (previa confirmación) para actualizar los registros.

---

## 6. Control de Stock

Permite el control y actualización del inventario:

### Consulta y Búsqueda

- Abra la **Ventana de Stock**.
- Se muestra una tabla con productos, incluyendo **ID, Nombre, Precio y Stock**.
- Un campo de búsqueda permite filtrar productos.

### Alta y Actualización

- Para **Agregar** un producto, complete el formulario con Nombre, Precio y Stock.
- Si el producto existe, se suma la nueva cantidad al stock actual y se actualiza el precio (con diálogo de conflicto, si es necesario).

### Eliminación

- Seleccione un producto y, tras una confirmación, elimínelo del inventario.

---

## 7. Gestión de Ventas

Este módulo abarca el proceso de venta completo, de la selección de productos a la generación de documentos.

### Creación y Gestión del Carrito

- Desde el **Panel de Productos**, seleccione el producto deseado y ajuste la **cantidad**.
- Pulse **"Agregar al Carrito"** para incluirlo en la compra.
- En el **Panel del Carrito** se detalla el listado de productos (ID, Producto, Precio Unitario, Cantidad y Subtotal).
- Se ofrecen controles para modificar o eliminar productos del carrito, incluyendo la aplicación de descuentos.

### Confirmación de Venta

- Al pulsar **"Confirmar Venta"**, el sistema valida stock y actualiza la base de datos, descontando unidades de los lotes.
- Se genera una factura utilizando una plantilla DOCX (convertida a PDF para su descarga).
- Opcionalmente, si se configura la generación de remito, se genera y asocia a un cliente.

### Requisitos Adicionales para Facturación y Remitos

**Importante:**  
Para la **generación de facturas y remitos** se requiere que el usuario tenga instalado Microsoft Word y que este se haya abierto recientemente, ya que la conversión de DOCX a PDF depende de la funcionalidad de Word.

---

## Instalación y Ejecución

1. **Base de Datos:**  
   Asegúrese de que MySQL (o XAMPP) esté en funcionamiento.

2. **Inicialización:**  
   Ejecute `principal.py` desde el directorio raíz del proyecto.  
   En la primera ejecución se crearán la base de datos y las tablas, y se migrarán los registros del vademécum.

3. **Inicio de Sesión:**  
   Inicie sesión con sus credenciales.  
   Los administradores tienen acceso a funcionalidades ampliadas (gestión de usuarios).