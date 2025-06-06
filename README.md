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
* [mysql.connector](https://pypi.org/project/mysql-connector-python/)
* [customtkinter](https://pypi.org/project/customtkinter/)
* [CTkMessagebox](https://pypi.org/project/CTkMessagebox/)
* [Pillow](https://pypi.org/project/pillow/)
* [docxtpl](https://pypi.org/project/docxtpl/)
* [docx2pdf](https://pypi.org/project/docx2pdf/)
* [docx.shared](https://pypi.org/project/python-docx/)

## Síntesis
Sistema informático programado en Python para utilizarse en el contexto de una farmacia.

Este proyecto se ha realizado por medio de la aplicación de la metodología ágil "Programación Extrema" (XP), a través de la herramienta [Trello](https://trello.com/).

## Participantes
- Alumnos (Programadores):
  - Matías Daniel Chiacchio
  - Luis Ariel Espinoza
  - Fabrizio Manuel Mansilla

- Profesores:
  - Cristian Fernando Cerquand
  - Johanna Motta

# Manual de Usuario

## 1. Inicio Rápido

1. **Inicie XAMPP:**  
   Antes de ejecutar el programa, abra XAMPP (o su servicio MySQL) para asegurarse de que el servidor esté activo.

2. **Ejecute la Aplicación:**  
   Ejecute `principal.py` desde el directorio raíz del proyecto.  
   Al iniciarse, el sistema:
   - Inicializa la conexión a la base de datos.
   - Crea la base de datos y las tablas necesarias (si es la primera ejecución).
   - Abre la pantalla de Login.

---

## 2. Pantalla de Login

La **Pantalla de Login** es la puerta de entrada a Farmanaccio.

- **Campos de Usuario y Contraseña:**  
  Ingrese sus credenciales. Si se dejan campos vacíos, aparecerá una advertencia.

- **Botón "Ingresar":**  
  Al pulsarlo, el sistema valida las credenciales ingresadas consultando la base de datos.

---

## 3. Ventana Principal

Tras un inicio de sesión exitoso se desplegará la **Ventana Principal** que centraliza el acceso a los módulos del sistema.

- **Botón de Usuario:**  
  Ubicado en la esquina superior izquierda; muestra el usuario activo. Al hacer clic, se despliega un menú con opciones para:
  - Agregar un nuevo usuario.
  - Administrar usuarios (solo para administradores).
  - Cerrar sesión.

- **Acceso a Módulos:**  
  En el área central encontrará botones para:
  - **Control de Stock**
  - **Gestión de Ventas**
  - **Gestión de Clientes**

---

## 4. Gestión de Usuarios

Este módulo permite administrar los usuarios del sistema.

### Agregar Usuario

- Seleccione **"(+) Agregar usuario"** desde el menú desplegable del botón de usuario.
- Complete el formulario:
  - **Nombre de Usuario**
  - **Contraseña** (puede alternar la visibilidad con “👁” o “🚫”)
  - **Rol:** Seleccione entre *admin* o *empleado*.
- Pulse **"Guardar"**.  
  El sistema valida que la contraseña tenga al menos 5 caracteres y que todos los campos sean llenados correctamente.

### Administrar Usuarios

- Seleccione **"Administrar usuarios"** para ver la lista de usuarios en una tabla que muestra:
  - **ID, Usuario, Contraseña, Rol y Acciones**.
- Para **Modificar** un usuario, edite la información en el formulario y pulse **"Modificar"**.
- Para **Eliminar** un usuario, haga clic en **"Eliminar"** y confirme la acción mediante una ventana emergente.

---

## 5. Gestión de Clientes

El módulo de clientes permite gestionar toda la información de sus clientes.

### Registro y Consulta

- Acceda a través del botón **"Gestión de Clientes"** en la Ventana Principal.
- La pantalla muestra:
  - Un campo de búsqueda para filtrar clientes por **Nombre, Apellido o CUIL**.
  - Una tabla con los clientes registrados, incluyendo **ID, Nombre, Apellido, CUIL, Teléfono, Email y Dirección**.

### Edición y Eliminación

- Seleccione un cliente de la tabla para cargar sus datos en el formulario.
- Realice las modificaciones y pulse:
  - **"Modificar"** para actualizar, o
  - **"Eliminar"** para borrar el registro (previa confirmación).

---

## 6. Control de Stock

El módulo de stock es esencial para el control del inventario.

### Consulta y Búsqueda

- Abra la **Ventana de Stock** desde la Ventana Principal.
- Se mostrará una tabla con los productos (columnas: **ID, Nombre, Precio, Stock**) y un campo de búsqueda.

### Alta y Actualización

- Para **Agregar** un producto, complete el formulario con:
  - **Nombre**
  - **Precio**
  - **Stock**
- Pulse **"Agregar Producto"**.  
  Si el producto ya existe, el sistema suma la cantidad al stock actual y actualiza el precio.
- Para **Modificar** un producto, seleccione el producto en la tabla, edite los datos y pulse **"Modificar Producto"**.

### Eliminación

- Seleccione el producto y, tras confirmar mediante una ventana emergente, elimínelo del inventario.

---

## 7. Gestión de Ventas

Este módulo abarca todo el proceso de venta, desde la selección del producto hasta la generación de la factura.

### Creación y Consulta del Carrito

- Desde el **Panel de Productos**, busque y seleccione el producto deseado.
- Ajuste la **cantidad** y pulse **"Agregar al Carrito"** para incluir el producto en la venta.
- El **Panel del Carrito** mostrará una tabla con los productos añadidos que incluye:
  - **ID, Producto, Precio Unitario, Cantidad y Subtotal**.

### Modificación del Carrito

- Utilice los controles (botones “+” y “−”) para ajustar la cantidad, o elimine productos del carrito.
- El sistema recalcula automáticamente el total, aplicando descuentos si se indican.

### Confirmación de Venta y Generación de Facturas

- Presione **"Confirmar Venta"** para finalizar la compra.
- El sistema verificará que el stock sea suficiente y actualizará la base de datos, descontando las cantidades vendidas.
- Se generará una factura utilizando una plantilla DOCX y se convertirá a PDF. Se le pedirá elegir la ubicación de guardado y se mostrará una notificación de éxito.

---

