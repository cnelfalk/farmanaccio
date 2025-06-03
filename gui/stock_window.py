# src/gui/stock_window.py
import customtkinter as ctk
from gui.login import icono_logotipo
from tkinter import ttk, messagebox
from mysql.connector import Error
from utils.utilidades import Utilidades

# Importamos la clase refactorizada para la gestión de stock
from logica.gestor_stock import StockManager

class StockWindow(ctk.CTkToplevel):
    """
    Ventana secundaria para el control de stock de productos.
    Permite buscar, agregar, modificar y eliminar productos.
    Los datos se muestran en un Treeview y se utiliza un formulario para escribir o editar los datos.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Control de Stock")
        self.resizable(False, False)

        # Dimensiones de la ventana
        window_width = 800
        window_height = 600

        # Calcular la posición para centrar la ventana
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Instanciar el gestor de stock (nuestra nueva clase que centraliza la lógica de productos)
        self.stock_manager = StockManager()

        # -------------------- Área de Búsqueda --------------------
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(padx=10, pady=5, expand=True)
        self.search_frame_inside = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        self.search_frame_inside.pack(padx=5)
        self.entry_search = ctk.CTkEntry(self.search_frame_inside, width=500, placeholder_text="Buscar producto...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 50))
        self.btn_search = ctk.CTkButton(self.search_frame_inside, text="Buscar", command=self.buscar_productos)
        self.btn_search.pack(side="left")

        # -------------------- Área del Treeview --------------------
        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=(5, 10))
        # Configurar el Treeview para mostrar productos
        self.tree = ttk.Treeview(frame_tabla, columns=("ID", "Nombre", "Precio", "Stock"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Stock", text="Stock")
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=200)
        self.tree.column("Precio", width=100)
        self.tree.column("Stock", width=100)
        self.tree.pack(side="left", padx=(10, 5), pady=10, expand=True, fill="both")
        self.tree.bind("<<TreeviewSelect>>", self.cargar_datos_seleccionados)
        scrollbar = ctk.CTkScrollbar(frame_tabla, orientation="vertical")
        scrollbar.configure(command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # -------------------- Formulario de Edición --------------------
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(padx=100, expand=True)
        # Campo nombre
        ctk.CTkLabel(self.frame_form, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_nombre = ctk.CTkEntry(self.frame_form, width=400)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)
        # Campo precio
        ctk.CTkLabel(self.frame_form, text="Precio:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_precio = ctk.CTkEntry(self.frame_form, width=400)
        self.entry_precio.grid(row=1, column=1, padx=5, pady=5)
        # Campo stock
        ctk.CTkLabel(self.frame_form, text="Stock:").grid(row=2, column=0, padx=10, pady=5)
        self.frame_stock = ctk.CTkFrame(self.frame_form)
        self.frame_stock.grid(row=2, column=1, padx=5, pady=5)
        self.btn_decrementar = ctk.CTkButton(self.frame_stock, text="-", width=30, command=self.decrementar_stock)
        self.btn_decrementar.pack(side="left")
        self.entry_stock = ctk.CTkEntry(self.frame_stock, width=250)
        self.entry_stock.pack(side="left")
        self.btn_incrementar = ctk.CTkButton(self.frame_stock, text="+", width=30, command=self.incrementar_stock)
        self.btn_incrementar.pack(side="left")

        # -------------------- Botones de Acción --------------------
        self.frame_btns = ctk.CTkFrame(self.frame_form, fg_color="#2E2E2E")
        self.frame_btns.grid(row=4, column=0, columnspan=2, pady=10)
        self.btn_agregar = ctk.CTkButton(self.frame_btns, text="Agregar Producto", command=self.agregar)
        self.btn_agregar.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.btn_modificar = ctk.CTkButton(self.frame_btns, text="Modificar Producto", command=self.modificar)
        self.btn_modificar.grid(row=1, column=0, padx=5, pady=5)
        self.btn_eliminar = ctk.CTkButton(self.frame_btns, text="Eliminar Producto", command=self.eliminar)
        self.btn_eliminar.grid(row=1, column=1, padx=5, pady=5)

        # Botón para cerrar la ventana
        self.btn_volver = ctk.CTkButton(self, text="Volver", command=self.destroy)
        self.btn_volver.pack(padx=5, pady=(0, 8))
        
        # Cargar los productos en el Treeview
        self.cargar_productos()

        # Establece el ícono tras 150ms
        self.after(150, lambda: self.iconbitmap(icono_logotipo))

    def buscar_productos(self):
        """
        Utiliza el término ingresado en el entry para buscar productos en la base de datos.
        Se filtra la lista de productos obtenida del StockManager.
        """
        termino = self.entry_search.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            # Si StockManager no tiene 'buscar_productos', se filtran los productos aquí:
            productos = [
                producto for producto in self.stock_manager.obtener_productos()
                if termino.lower() in producto["nombre"].lower()
            ]
            for producto in productos:
                self.tree.insert("", "end", values=(
                    producto["prodId"], producto["nombre"], producto["precio"], producto["stock"]
                ))
        except Exception as e:
            print("Error al buscar productos:", e)

    
    def cargar_productos(self):
        """
        Recupera todos los productos utilizando el método 'obtener_productos' del StockManager
        y los muestra en el Treeview.
        """
        for i in self.tree.get_children():
            self.tree.delete(i)
        productos = self.stock_manager.obtener_productos()
        for producto in productos:
            self.tree.insert("", "end", values=(
                producto["prodId"], producto["nombre"], producto["precio"], producto["stock"]
            ))
            
    def agregar(self):
        """
        Captura los datos del formulario (nombre, precio y stock), los convierte a los tipos correctos
        y llama al método 'agregar_o_actualizar_producto' del StockManager.
        Si la acción es confirmada, se recarga el Treeview.
        """
        try:
            producto = {
                "nombre": self.entry_nombre.get().strip(),
                "precio": float(self.entry_precio.get()),
                "stock": int(self.entry_stock.get())
            }
        except ValueError:
            messagebox.showerror("Error", "Precio y Stock deben ser numéricos.", parent=self)
            return
        if Utilidades.confirmar_accion(self, "agregar este producto", tipo_usuario="administrador"):
            if self.stock_manager.agregar_o_actualizar_producto(producto):
                messagebox.showinfo("Éxito", "Producto agregado/actualizado exitosamente!", parent=self)
                self.cargar_productos()
            else:
                messagebox.showerror("Error", "No se pudo agregar/actualizar el producto.", parent=self)
    
    def modificar(self):
        """
        Valida que el producto seleccionado en el Treeview sea modificado
        con los nuevos datos ingresados en el formulario. Se llama al método
        'modificar_producto' del StockManager para actualizar la base de datos.
        """
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un producto para modificar.", parent=self)
            return
        values = self.tree.item(selected_item, "values")
        id_producto = values[0]
        try:
            producto_actualizado = {
                "nombre": self.entry_nombre.get().strip(),
                "precio": float(self.entry_precio.get()),
                "stock": int(self.entry_stock.get())
            }
        except ValueError:
            messagebox.showerror("Error", "Precio y Stock deben ser numéricos.", parent=self)
            return
        if Utilidades.confirmar_accion(self, "modificar este producto", tipo_usuario="administrador"):
            if self.stock_manager.modificar_producto(self, id_producto, producto_actualizado):
                messagebox.showinfo("Éxito", "Producto modificado exitosamente!", parent=self)
                self.cargar_productos()
            else:
                messagebox.showerror("Error", "Error al modificar producto.", parent=self)
        
    def eliminar(self):
        """
        Permite eliminar el producto seleccionado en el Treeview.
        Se confirma la acción y, en caso afirmativo, se llama al método 'eliminar_producto'
        del StockManager. Luego se recarga la lista de productos.
        """
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un producto para eliminar.", parent=self)
            return
        values = self.tree.item(selected_item, "values")
        id_producto = values[0]
        if Utilidades.confirmar_accion(self, "eliminar este producto", tipo_usuario="administrador"):
            if self.stock_manager.eliminar_producto(id_producto):
                messagebox.showinfo("Éxito", "Producto eliminado exitosamente!", parent=self)
                self.cargar_productos()
            else:
                messagebox.showerror("Error", "Error al eliminar producto.", parent=self)
    
    def cargar_datos_seleccionados(self, event):
        """
        Al seleccionar un producto en el Treeview, carga sus datos en los campos del formulario
        para permitir su edición.
        """
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, values[1])
            self.entry_precio.delete(0, "end")
            self.entry_precio.insert(0, values[2])
            self.entry_stock.delete(0, "end")
            self.entry_stock.insert(0, values[3])
    
    def incrementar_stock(self):
        """
        Incrementa en 1 el valor actual del campo "Stock". Si el valor ingresado no es numérico,
        se asume que es 0.
        """
        try:
            current_stock = int(self.entry_stock.get())
        except ValueError:
            current_stock = 0
        new_stock = current_stock + 1
        self.entry_stock.delete(0, "end")
        self.entry_stock.insert(0, new_stock)

    def decrementar_stock(self):
        """
        Decrementa en 1 el valor actual del campo "Stock", asegurándose de que no sea menor a 0.
        """
        try:
            current_stock = int(self.entry_stock.get())
        except ValueError:
            current_stock = 0
        new_stock = current_stock - 1 if current_stock > 0 else 0
        self.entry_stock.delete(0, "end")
        self.entry_stock.insert(0, new_stock)

# Ejemplo de uso:
if __name__ == "__main__":
    # Se simula un usuario logueado, por ejemplo:
    app = StockWindow()
    app.mainloop()