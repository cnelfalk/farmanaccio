# src/gui/admin_usuarios_window.py

from tkinter import StringVar
import customtkinter as ctk
import tkinter.messagebox as messagebox
from customtkinter import CTkToplevel, CTkScrollableFrame
from logica.gestor_usuarios import UsuarioManager
from PIL import Image  # Asegurate de importarlo también
from gui.login import icono_logotipo

class AdminUsuariosWindow(CTkToplevel):
    def __init__(self, parent, usuario_actual):
        super().__init__(parent)
        self.title("Administrar Usuarios")
        self.grab_set()
        self.resizable(False, False)

        # Definir dimensiones de la ventana y centrarla
        window_width = 630
        window_height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.usuario_actual = usuario_actual
        self.usuario_manager = UsuarioManager()

        # Combobox para filtrar por estado (Activos/Inactivos)
        self.filter_var = StringVar(value="Activos")
        self.filter_combobox = ctk.CTkComboBox(
            self,
            values=["Activos", "Inactivos"],
            variable=self.filter_var,  # Vinculación de la variable
            width=150,
            command=self.cargar_usuarios
        )
        self.filter_combobox.pack(pady=(10, 0))

        # CTkScrollableFrame con fondo de color verde oscuro.
        # Se pasan explícitamente fg_color y label_fg_color para evitar KeyError en el tema.
        self.tabla_frame = CTkScrollableFrame(
            self, 
            height=300,
            fg_color="#003300",
            label_fg_color="#003300"
        )
        self.tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Inicialmente se dibujan los encabezados (esto se usa si hay usuarios)
        self._dibujar_encabezados()

        self.cargar_usuarios()

        # Botón de Volver centrado en la parte inferior
        self.btn_volver = ctk.CTkButton(self, text="Volver", command=self.destroy, width=150)
        self.btn_volver.pack(pady=(0, 10))
        
        self.after(200, lambda: self.iconbitmap(icono_logotipo))
    
    def _dibujar_encabezados(self):
        """Dibuja los encabezados de la “tabla” en el scrollable frame."""
        self.labels = ["ID", "Usuario", "Contraseña", "Rol", "Acciones"]
        # Borramos los hijos existentes del frame
        for widget in self.tabla_frame.winfo_children():
            widget.destroy()
        for i, texto in enumerate(self.labels):
            label = ctk.CTkLabel(self.tabla_frame, text=texto, font=("Arial", 12, "bold"), fg_color="#003300")
            label.grid(row=0, column=i, padx=5, pady=5)
    
    def cargar_usuarios(self, *args):
        filtro = self.filter_var.get()
        activo = 1 if filtro == "Activos" else 0
        usuarios = self.usuario_manager.obtener_usuarios_por_estado(activo)
        
        # Si estamos en "Inactivos" y no hay registros, limpiar el frame y mostrar mensaje
        if filtro == "Inactivos" and not usuarios:
            for widget in self.tabla_frame.winfo_children():
                widget.destroy()
            mensaje = ctk.CTkLabel(self.tabla_frame, text="No se encuentran usuarios inactivos.", 
                                    font=("Arial", 12), fg_color="#003300")
            mensaje.pack(expand=True, pady=20)
            return
        # Si hay usuarios, aseguramos que se muestren los encabezados
        self._dibujar_encabezados()
        
        # Limpiar las filas de datos que pudieran existir (desde la fila 1)
        for widget in self.tabla_frame.winfo_children():
            info = widget.grid_info()
            # Saltar la fila 0 (encabezados)
            if int(info.get("row", 0)) > 0:
                widget.destroy()
        
        # Listar los usuarios, cada uno en una fila a partir de la fila 1.
        for i, usuario in enumerate(usuarios, start=1):
            id_ = usuario["userId"]
            nombre = usuario["usuario"]
            password = usuario["password"]
            rol = usuario["role"]

            label_id = ctk.CTkLabel(self.tabla_frame, text=str(id_), fg_color="#003300")
            label_id.grid(row=i, column=0, padx=5, pady=5)

            entry_usuario = ctk.CTkEntry(self.tabla_frame)
            entry_usuario.insert(0, nombre)
            entry_usuario.grid(row=i, column=1, padx=5, pady=5)

            entry_password = ctk.CTkEntry(self.tabla_frame)
            entry_password.insert(0, password)
            entry_password.grid(row=i, column=2, padx=5, pady=5)

            combo_rol = ctk.CTkComboBox(self.tabla_frame, values=["admin", "empleado"], width=120)
            combo_rol.set(rol.lower())
            combo_rol.grid(row=i, column=3, padx=5, pady=5)

            if filtro == "Activos":
                if nombre == self.usuario_actual:
                    combo_rol.configure(state="disabled")
                btn_mod = ctk.CTkButton(
                    self.tabla_frame, text="Modificar", width=10,
                    command=lambda i=i, id_=id_: self.modificar_usuario(i, id_)
                )
                btn_mod.grid(row=i, column=4, padx=2, pady=5)

                btn_del = ctk.CTkButton(
                    self.tabla_frame, text="Eliminar", fg_color="red", width=10,
                    command=lambda id_=id_: self.eliminar_usuario(id_)
                )
                btn_del.grid(row=i, column=5, padx=2, pady=5)
            else:
                btn_restaurar = ctk.CTkButton(
                    self.tabla_frame, text="Restaurar Usuario", fg_color="green", width=15,
                    command=lambda id_=id_: self.restaurar_usuario(id_)
                )
                btn_restaurar.grid(row=i, column=4, columnspan=2, padx=5, pady=5)

    def modificar_usuario(self, fila, id_):
        nuevo_usuario = self.tabla_frame.grid_slaves(row=fila, column=1)[0].get()
        nuevo_password = self.tabla_frame.grid_slaves(row=fila, column=2)[0].get()
        nuevo_rol = self.tabla_frame.grid_slaves(row=fila, column=3)[0].get().strip().lower()
        usuarios = self.usuario_manager.obtener_usuarios_por_estado(1)
        original_usuario = None
        for u in usuarios:
            if u["userId"] == id_:
                original_usuario, original_password, original_rol = u["usuario"], u["password"], u["role"]
                break
        if original_usuario is None:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return
        if len(nuevo_password) < 5:
            messagebox.showerror("Error", "La contraseña debe tener mínimo 5 caracteres.")
            return
        if (nuevo_usuario == original_usuario and
            nuevo_password == original_password and
            nuevo_rol == original_rol):
            messagebox.showinfo("Sin cambios", "No se detectaron cambios para actualizar.")
            return
        if nuevo_rol not in ("admin", "empleado"):
            messagebox.showwarning("Rol inválido", "El rol debe ser 'admin' o 'empleado'.")
            return
        if self.usuario_manager.actualizar_usuario(id_, nuevo_usuario, nuevo_password, nuevo_rol):
            messagebox.showinfo("Éxito", "Usuario actualizado.")
            self.cargar_usuarios()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el usuario.")

    def eliminar_usuario(self, id_):
        usuarios = self.usuario_manager.obtener_usuarios_por_estado(1)
        usuario_a_eliminar = None
        for u in usuarios:
            if u["userId"] == id_:
                usuario_a_eliminar = u["usuario"]
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
            if self.usuario_manager.eliminar_usuario(id_):
                messagebox.showinfo("Éxito", "Usuario eliminado.")
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario.")

    def restaurar_usuario(self, id_):
        if messagebox.askyesno("Confirmar", "¿Desea restaurar este usuario?"):
            if self.usuario_manager.restaurar_usuario(id_):
                messagebox.showinfo("Éxito", "Usuario restaurado.")
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", "No se pudo restaurar el usuario.")


if __name__ == "__main__":
    import sys
    import os
    from tkinter import Tk
    import tkinter.font as tkFont

    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    if src_root not in sys.path:
        sys.path.insert(0, src_root)

    root = Tk()
    root.withdraw()
    app = AdminUsuariosWindow(root, "admin")
    app.mainloop()
