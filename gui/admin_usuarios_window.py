# src/gui/admin_usuarios_window.py

from utils.utilidades import CTkPromptArchivado
from tkinter import StringVar, simpledialog, messagebox
import customtkinter as ctk
from customtkinter import CTkToplevel, CTkScrollableFrame
from logica.gestor_usuarios import UsuarioManager
from gui.login import icono_logotipo

class AdminUsuariosWindow(CTkToplevel):
    def __init__(self, parent, usuario_actual):
        super().__init__(parent)
        self.title("Administrar Usuarios")
        self.grab_set()
        self.resizable(False, False)

        # Centrar la ventana
        window_width, window_height = 630, 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.usuario_actual = usuario_actual
        self.usuario_manager = UsuarioManager()
        self.inactive_user_roles = {}

        # Combobox para filtrar Activos/Inactivos
        self.filter_var = StringVar(value="Activos")
        self.filter_combobox = ctk.CTkComboBox(
            self,
            values=["Activos", "Inactivos"],
            variable=self.filter_var,
            width=150,
            command=self.cargar_usuarios
        )
        self.filter_combobox.pack(pady=(10, 0))

        # Frame scrollable para la “tabla”
        self.tabla_frame = CTkScrollableFrame(
            self,
            height=300,
            fg_color="#003300",
            label_fg_color="#003300"
        )
        self.tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._dibujar_encabezados()
        self.cargar_usuarios()

        # Botón Volver
        self.btn_volver = ctk.CTkButton(
            self, text="Volver", width=150, command=self.destroy
        )
        self.btn_volver.pack(pady=(0, 10))

        self.after(200, lambda: self.iconbitmap(icono_logotipo))

    def _dibujar_encabezados(self):
        for widget in self.tabla_frame.winfo_children():
            widget.destroy()
        labels = ["ID", "Usuario", "Contraseña", "Rol", "Acciones"]
        for col, txt in enumerate(labels):
            ctk.CTkLabel(
                self.tabla_frame,
                text=txt,
                font=("Arial", 12, "bold"),
                fg_color="#003300"
            ).grid(row=0, column=col, padx=5, pady=5)

    def cargar_usuarios(self, *args):
        estado = 1 if self.filter_var.get() == "Activos" else 0
        usuarios = self.usuario_manager.obtener_usuarios_por_estado(estado)

        # Si no hay usuarios inactivos, mostrar mensaje
        if estado == 0 and not usuarios:
            for w in self.tabla_frame.winfo_children():
                w.destroy()
            ctk.CTkLabel(
                self.tabla_frame,
                text="No hay usuarios inactivos.",
                font=("Arial", 12),
                fg_color="#003300"
            ).pack(expand=True, pady=20)
            return

        self._dibujar_encabezados()
        # Borrar filas previas
        for w in list(self.tabla_frame.winfo_children()):
            info = w.grid_info()
            if info and info["row"] > 0:
                w.destroy()
        self.inactive_user_roles.clear()

        for i, u in enumerate(usuarios, start=1):
            uid = u["userID"]
            nombre = u["usuario"]
            pw     = u["password"]
            rol    = u["role"]

            # ID
            ctk.CTkLabel(
                self.tabla_frame, text=str(uid), fg_color="#003300"
            ).grid(row=i, column=0, padx=5, pady=5)

            # Usuario / Contraseña / Rol
            ent_u = ctk.CTkEntry(self.tabla_frame)
            ent_u.insert(0, nombre)
            ent_u.grid(row=i, column=1, padx=5, pady=5)

            ent_p = ctk.CTkEntry(self.tabla_frame)
            ent_p.insert(0, pw)
            ent_p.grid(row=i, column=2, padx=5, pady=5)

            cb_r = ctk.CTkComboBox(
                self.tabla_frame, values=["admin", "empleado"], width=120
            )
            cb_r.set(rol)
            cb_r.grid(row=i, column=3, padx=5, pady=5)

            if estado == 1:  # ACTIVOS → Botones Modificar / Archivar
                if nombre == self.usuario_actual:
                    cb_r.configure(state="disabled")
                ctk.CTkButton(
                    self.tabla_frame,
                    text="Modificar",
                    width=10,
                    command=lambda row=i, id_=uid: self.modificar_usuario(row, id_)
                ).grid(row=i, column=4, padx=2, pady=5)
                ctk.CTkButton(
                    self.tabla_frame,
                    text="Archivar",
                    fg_color="red",
                    width=10,
                    command=lambda id_=uid: self.eliminar_usuario(id_)
                ).grid(row=i, column=5, padx=2, pady=5)

            else:  # INACTIVOS → Botón Restaurar
                self.inactive_user_roles[uid] = cb_r
                ctk.CTkButton(
                    self.tabla_frame,
                    text="Restaurar",
                    fg_color="green",
                    width=15,
                    command=lambda id_=uid: self.restaurar_usuario(id_)
                ).grid(row=i, column=4, columnspan=2, padx=5, pady=5)

    def modificar_usuario(self, row, id_):
        ent_u = self.tabla_frame.grid_slaves(row=row, column=1)[0].get().strip()
        ent_p = self.tabla_frame.grid_slaves(row=row, column=2)[0].get().strip()
        ent_r = self.tabla_frame.grid_slaves(row=row, column=3)[0].get().strip().lower()

        if len(ent_p) < 5:
            messagebox.showerror("Error", "La contraseña debe tener al menos 5 caracteres.")
            return
        if ent_r not in ("admin", "empleado"):
            messagebox.showwarning("Error", "Rol inválido.")
            return

        ok = self.usuario_manager.actualizar_usuario(id_, ent_u, ent_p, ent_r)
        if ok:
            messagebox.showinfo("Éxito", "Usuario modificado.")
            self.cargar_usuarios()
        else:
            messagebox.showerror("Error", "No se pudo modificar el usuario.")

    def eliminar_usuario(self, id_):
        prompt = CTkPromptArchivado(parent=self)
        razon = prompt.resultado
        if razon is None:  # Cancelado
            return

        ok = self.usuario_manager.eliminar_usuario(id_, razon.strip())
        if ok:
            messagebox.showinfo("Éxito", "Usuario archivado.")
            self.cargar_usuarios()
        else:
            messagebox.showerror("Error", "No se pudo archivar el usuario.")

    def restaurar_usuario(self, id_):
        nuevo_rol = self.inactive_user_roles[id_].get().strip().lower()
        if not nuevo_rol:
            messagebox.showerror("Error", "No se pudo determinar el nuevo rol.")
            return
        if messagebox.askyesno("Confirmar", f"¿Restaurar usuario con rol '{nuevo_rol}'?"):
            ok = self.usuario_manager.restaurar_usuario(id_, nuevo_rol)
            if ok:
                messagebox.showinfo("Éxito", "Usuario restaurado.")
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", "No se pudo restaurar el usuario.")
