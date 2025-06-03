# src/gui/admin_usuarios_window.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
from customtkinter import CTkToplevel
from gui.login import icono_logotipo
from logica.gestor_usuarios import UsuarioManager  # Actualizado: se importa la clase

class AdminUsuariosWindow(CTkToplevel):
    def __init__(self, parent, usuario_actual):
        super().__init__(parent)
        self.title("Administrar Usuarios")
        self.grab_set()
        self.resizable(False, False)

        self.usuario_actual = usuario_actual
        # Instanciamos la clase UsuarioManager
        self.usuario_manager = UsuarioManager()

        self.tabla_frame = ctk.CTkFrame(self)
        self.tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.labels = ["ID", "Usuario", "Contraseña", "Rol", "Acciones"]
        for i, texto in enumerate(self.labels):
            label = ctk.CTkLabel(self.tabla_frame, text=texto, font=("Arial", 12, "bold"))
            label.grid(row=0, column=i, padx=5, pady=5)

        self.cargar_usuarios()

        # Aseguramos que se establezca el ícono con iconbitmap tras 100ms
        self.after(200, lambda: self.iconbitmap(icono_logotipo))

    def cargar_usuarios(self):
        # Limpiamos los widgets de la tabla excepto la cabecera
        for widget in self.tabla_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        # Llamamos al método de la clase para obtener los usuarios
        usuarios = self.usuario_manager.obtener_usuarios()
        for i, usuario in enumerate(usuarios, start=1):
            id_, nombre, password, rol = usuario

            # Mostrar el ID como etiqueta (no editable)
            label_id = ctk.CTkLabel(self.tabla_frame, text=str(id_))
            label_id.grid(row=i, column=0, padx=5, pady=5)

            entry_usuario = ctk.CTkEntry(self.tabla_frame)
            entry_usuario.insert(0, nombre)
            entry_usuario.grid(row=i, column=1)

            entry_password = ctk.CTkEntry(self.tabla_frame)
            entry_password.insert(0, password)
            entry_password.grid(row=i, column=2)

            combo_rol = ctk.CTkComboBox(self.tabla_frame, values=["admin", "empleado"], width=120)
            combo_rol.set(rol.lower())
            combo_rol.grid(row=i, column=3)

            # Deshabilitar el cambio de rol si es el usuario actual
            if nombre == self.usuario_actual:
                combo_rol.configure(state="disabled")

            btn_mod = ctk.CTkButton(
                self.tabla_frame, text="Modificar", width=10,
                command=lambda i=i, id_=id_: self.modificar_usuario(i, id_)
            )
            btn_mod.grid(row=i, column=4, padx=2)

            btn_del = ctk.CTkButton(
                self.tabla_frame, text="Eliminar", fg_color="red", width=10,
                command=lambda id_=id_: self.eliminar_usuario(id_)
            )
            btn_del.grid(row=i, column=5, padx=2)

    def modificar_usuario(self, fila, id_):
        # Extraer los nuevos valores de los widgets
        nuevo_usuario = self.tabla_frame.grid_slaves(row=fila, column=1)[0].get()
        nuevo_password = self.tabla_frame.grid_slaves(row=fila, column=2)[0].get()
        nuevo_rol = self.tabla_frame.grid_slaves(row=fila, column=3)[0].get().strip().lower()

        # Obtener los datos originales usando el método actualizado
        usuarios = self.usuario_manager.obtener_usuarios()
        original_usuario = None
        for u in usuarios:
            if u[0] == id_:
                original_usuario, original_password, original_rol = u[1], u[2], u[3]
                break

        if original_usuario is None:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return

        if len(nuevo_password) < 5:
            messagebox.showerror("Error", "No puede ingresar una contraseña menor a cinco carácteres.")
            return

        # Comparar si hubo cambios
        if (nuevo_usuario == original_usuario and
            nuevo_password == original_password and
            nuevo_rol == original_rol):
            messagebox.showinfo("Sin cambios", "No se detectaron cambios para actualizar.")
            return

        if nuevo_rol not in ("admin", "empleado"):
            messagebox.showwarning("Rol inválido", "Debe ser 'admin' o 'empleado'")
            return

        # Llamar al método de actualización de la clase UsuarioManager
        if self.usuario_manager.actualizar_usuario(id_, nuevo_usuario, nuevo_password, nuevo_rol):
            messagebox.showinfo("Éxito", "Usuario actualizado")
            self.cargar_usuarios()
        else:
            messagebox.showerror("Error", "No se pudo actualizar. Asegúrese de que los datos sean válidos.")

    def eliminar_usuario(self, id_):
        usuarios = self.usuario_manager.obtener_usuarios()

        # Buscar el nombre del usuario que se quiere eliminar
        usuario_a_eliminar = None
        for u in usuarios:
            if u[0] == id_:
                usuario_a_eliminar = u[1]
                break

        if usuario_a_eliminar is None:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return

        if usuario_a_eliminar == self.usuario_actual:
            messagebox.showwarning("Operación no permitida", "No puede eliminar el usuario con sesión activa.")
            return

        if len(usuarios) <= 1:
            messagebox.showwarning("Operación no permitida", "No puede eliminar el único usuario del sistema.")
            return

        if messagebox.askyesno("Confirmar", f"¿Seguro que desea eliminar al usuario '{usuario_a_eliminar}'?"):
            # Llamar al método de eliminación de la clase
            if self.usuario_manager.eliminar_usuario(id_):
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario.")

if __name__ == "__main__":
    import sys
    import os

    # Agregar el path raíz del proyecto (donde está "src") al sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    if src_root not in sys.path:
        sys.path.insert(0, src_root)

    import tkinter as tk
    from gui.admin_usuarios_window import AdminUsuariosWindow

    root = tk.Tk()
    root.withdraw()
    app = AdminUsuariosWindow(root, "admin")
    app.mainloop()

