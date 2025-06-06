# src/gui/clientes_window.py
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from logica.gestor_clientes import ClienteManager
from gui.login import icono_logotipo
import tkinter.font as tkFont

class ClientesWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gestión de Clientes")
        self.geometry("820x620")
        self.resizable(False, False)

        self.cliente_manager = ClienteManager()
        self.cliente_actual_id = None
        self.clientes_map = {}  # id → dict

        # ─── Búsqueda ──────────────────────────────────────────────────────
        self.frame_search = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_search.pack(fill="x", padx=10, pady=(10, 0))

        self.entry_search = ctk.CTkEntry(self.frame_search, placeholder_text="Buscar por Nombre, Apellido o CUIL...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_search = ctk.CTkButton(self.frame_search, text="Buscar", width=100, command=self._buscar_clientes)
        self.btn_search.pack(side="left", padx=5)

        self.btn_mostrar_todos = ctk.CTkButton(self.frame_search, text="Mostrar Todos", width=110, command=self._cargar_clientes)
        self.btn_mostrar_todos.pack(side="left", padx=5)

        # ─── Listado con scrollbars ────────────────────────────────────────
        self.frame_tree_outer = ctk.CTkFrame(self)
        self.frame_tree_outer.pack(fill="both", padx=10, pady=10, expand=False)

        self.frame_tree = ctk.CTkFrame(self.frame_tree_outer)
        self.frame_tree.pack(fill="both", expand=True)
        self.frame_tree.configure(height=260)  # altura fija

        cols = ("ID", "Nombre", "Apellido", "CUIL", "Teléfono", "Email", "Dirección")
        self.tree = ttk.Treeview(self.frame_tree, columns=cols, show="headings")
        for col in cols:
            anchor = "center" if col == "ID" else "w"
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=anchor)

        vsb = ttk.Scrollbar(self.frame_tree, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.frame_tree, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.frame_tree.rowconfigure(0, weight=1)
        self.frame_tree.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ─── Formulario ────────────────────────────────────────────────────
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(fill="x", padx=10, pady=(0, 10))

        fields = [
            ("nombre",   "Nombre"),
            ("apellido", "Apellido"),
            ("cuil",     "CUIL"),
            ("telefono", "Teléfono"),
            ("email",    "Email"),
            ("direccion","Dirección")
        ]
        self.entries = {}
        for i, (key, label) in enumerate(fields):
            ctk.CTkLabel(self.frame_form, text=f"{label}:").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            ent = ctk.CTkEntry(self.frame_form)
            ent.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            self.entries[key] = ent
        self.frame_form.grid_columnconfigure(1, weight=1)

        # ─── Botones CRUD ──────────────────────────────────────────────────
        self.frame_btns = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        self.frame_btns.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self.btn_agregar   = ctk.CTkButton(self.frame_btns, text="Agregar", width=100, command=self._agregar)
        self.btn_modificar = ctk.CTkButton(self.frame_btns, text="Modificar", width=100, command=self._modificar)
        self.btn_eliminar  = ctk.CTkButton(self.frame_btns, text="Eliminar", fg_color="red", width=100, command=self._eliminar)

        self.btn_agregar.grid(row=0, column=0, padx=5)
        self.btn_modificar.grid(row=0, column=1, padx=5)
        self.btn_eliminar.grid(row=0, column=2, padx=5)

        # ─── Botón Volver ──────────────────────────────────────────────────
        self.btn_volver = ctk.CTkButton(self, text="Volver", command=self.destroy, width=120)
        self.btn_volver.pack(pady=(0, 12))

        # Establece el ícono tras 150ms
        self.after(150, lambda: self.iconbitmap(icono_logotipo))

        # Carga inicial
        self._cargar_clientes()

    # ───────────────────────────────── CRUD y utilidades ─────────────────────────────────
    def _cargar_clientes(self):
        self._poblar_tree(self.cliente_manager.obtener_clientes())
        self._reset_form()

    def _poblar_tree(self, lista_clientes):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.clientes_map.clear()
        for c in lista_clientes:
            self.clientes_map[c["clienteId"]] = c
            self.tree.insert("", "end", values=(
                c["clienteId"], c["nombre"], c["apellido"], c["cuil"],
                c["telefono"], c["email"], c["direccion"]
            ))
        self._ajustar_ancho_id()

    def _buscar_clientes(self):
        term = self.entry_search.get().strip().lower()
        if not term:
            self._cargar_clientes()
            return
        filtrados = [
            c for c in self.cliente_manager.obtener_clientes()
            if term in c["nombre"].lower()
            or term in c["apellido"].lower()
            or term in c["cuil"].lower()
        ]
        self._poblar_tree(filtrados)

    def _ajustar_ancho_id(self):
        if not self.clientes_map:
            self.tree.column("ID", width=50)
            return
        max_digits = max(len(str(cid)) for cid in self.clientes_map)
        new_px = tkFont.Font().measure("0" * max_digits) + 16
        self.tree.column("ID", width=new_px)

    def _reset_form(self):
        self.cliente_actual_id = None
        for ent in self.entries.values():
            ent.delete(0, tk.END)
        self.btn_agregar.configure(state="normal")
        self.btn_modificar.configure(state="disabled")
        self.btn_eliminar.configure(state="disabled")

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        cid = int(self.tree.item(sel[0], "values")[0])
        c = self.clientes_map[cid]
        for k in self.entries:
            self.entries[k].delete(0, tk.END)
            self.entries[k].insert(0, c.get(k, ""))
        self.cliente_actual_id = cid
        self.btn_agregar.configure(state="disabled")
        self.btn_modificar.configure(state="normal")
        self.btn_eliminar.configure(state="normal")

    def _validar(self):
        if not (self.entries["nombre"].get().strip() and
                self.entries["apellido"].get().strip() and
                self.entries["cuil"].get().strip()):
            messagebox.showwarning("Atención", "Nombre, Apellido y CUIL son obligatorios.")
            return False
        return True

    def _agregar(self):
        if not self._validar(): return
        datos = {k: v.get().strip() for k, v in self.entries.items()}
        if self.cliente_manager.crear_cliente(datos):
            messagebox.showinfo("Éxito", "Cliente agregado.")
            self._cargar_clientes()
        else:
            messagebox.showerror("Error", "No se pudo agregar el cliente.")

    def _modificar(self):
        if self.cliente_actual_id is None or not self._validar(): return
        datos = {k: v.get().strip() for k, v in self.entries.items()}
        if self.cliente_manager.actualizar_cliente(self.cliente_actual_id, datos):
            messagebox.showinfo("Éxito", "Cliente actualizado.")
            self._cargar_clientes()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el cliente.")

    def _eliminar(self):
        if self.cliente_actual_id is None: return
        if messagebox.askyesno("Confirmar", "¿Eliminar este cliente?"):
            if self.cliente_manager.eliminar_cliente(self.cliente_actual_id):
                messagebox.showinfo("Éxito", "Cliente eliminado.")
                self._cargar_clientes()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el cliente.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    ClientesWindow(root).mainloop()