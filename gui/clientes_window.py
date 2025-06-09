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
        self.resizable(False, False)

        # Definir dimensiones de la ventana
        window_width = 900
        window_height = 565

        # Calcular la posición para centrar la ventana
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)

        # Establecer la geometría centrada
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.cliente_manager = ClienteManager()
        self.cliente_actual_id = None
        self.selected_cliente = None  # Nuevo atributo para almacenar el cliente seleccionado
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

        # ─── Treeview ──────────────────────────────────────────────────────
        self.frame_tree_outer = ctk.CTkFrame(self, fg_color="#823F2A")
        self.frame_tree_outer.pack(fill="both", padx=10, pady=10)

        # Frame con altura fija (~130px para 5 filas visibles)
        self.frame_tree = ctk.CTkFrame(self.frame_tree_outer, height=130)
        self.frame_tree.pack(fill="x", padx=10, pady=10, expand=False)
        self.frame_tree.pack_propagate(False)

        cols = ("ID", "Nombre", "Apellido", "CUIL", "Teléfono", "Email", "Dirección", "IVA")
        self.tree = ttk.Treeview(self.frame_tree, columns=cols, show="headings", height=5)
        for col in cols:
            anchor = "center" if col == "ID" else "w"
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=anchor)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        vsb = ctk.CTkScrollbar(self.frame_tree, orientation="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns", pady=10)
        hsb = ctk.CTkScrollbar(self.frame_tree, orientation="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.frame_tree.rowconfigure(0, weight=0)
        self.frame_tree.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ─── Formulario ────────────────────────────────────────────────────
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(fill="x", padx=10, pady=(0, 10))

        # Creamos dos subframes para las dos columnas
        self.left_frame = ctk.CTkFrame(self.frame_form, fg_color="#003D19")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 0))
        self.right_frame = ctk.CTkFrame(self.frame_form, fg_color="#003D19")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=(5, 0))

        # Se distribuye el espacio del formulario de forma equitativa
        self.frame_form.grid_columnconfigure(0, weight=1)
        self.frame_form.grid_columnconfigure(1, weight=1)

        self.entries = {}

        # Column izquierda con "Nombre", "Apellido" y "Teléfono"
        left_fields = [
            ("nombre",   "Nombre"),
            ("apellido", "Apellido"),
            ("telefono", "Teléfono")
        ]
        for i, (key, label_text) in enumerate(left_fields):
            # Se fija un ancho para el label (por ejemplo 100) y se centra sin que se expanda
            label = ctk.CTkLabel(self.left_frame, text=f"{label_text}:", anchor="center", width=100)
            label.grid(row=i, column=0, sticky="n", padx=5, pady=5)
            ent = ctk.CTkEntry(self.left_frame)
            ent.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            self.entries[key] = ent
        # Solo la columna de la entrada se expande
        self.left_frame.grid_columnconfigure(1, weight=1)

        # Column derecha con "CUIT-CUIL", "Dirección" y "E-mail"
        right_fields = [
            ("cuil",     "CUIT-CUIL"),
            ("direccion", "Dirección"),
            ("email",    "E-mail")
        ]
        for i, (key, label_text) in enumerate(right_fields):
            label = ctk.CTkLabel(self.right_frame, text=f"{label_text}:", anchor="center", width=100)
            label.grid(row=i, column=0, sticky="n", padx=5, pady=5)
            ent = ctk.CTkEntry(self.right_frame)
            ent.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            self.entries[key] = ent
        self.right_frame.grid_columnconfigure(1, weight=1)


        # Los demás elementos (por ejemplo, el frame del IVA) se redistribuyen en base a la nueva cantidad de filas.
        row_iva = 3  # Al tener tres filas por columna
        iva_frame = ctk.CTkFrame(self.frame_form, fg_color="#304C27")
        iva_frame.grid(row=1, column=0, columnspan=2, pady=5)
        iva_label = ctk.CTkLabel(iva_frame, text="IVA:", anchor="center")
        iva_label.pack(side="left", padx=5)
        opciones_iva = ["Exento", "Monotributo", "Resp. Insc.", "Eventual", "Cons. Final"]
        self.combobox_iva = ctk.CTkComboBox(iva_frame, values=opciones_iva, state="readonly", width=100)
        self.combobox_iva.set("")
        self.combobox_iva.pack(side="left", padx=5)

        self.frame_btns = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        self.frame_btns.grid(row=row_iva+1, column=0, columnspan=2, pady=10)

        self.btn_agregar   = ctk.CTkButton(self.frame_btns, text="Agregar", width=100, command=self._agregar)
        self.btn_modificar = ctk.CTkButton(self.frame_btns, text="Modificar", width=100, command=self._modificar)
        self.btn_eliminar  = ctk.CTkButton(self.frame_btns, text="Eliminar", fg_color="red", width=100, command=self._eliminar)

        self.btn_agregar.grid(row=0, column=0, padx=5)
        self.btn_modificar.grid(row=0, column=1, padx=5)
        self.btn_eliminar.grid(row=0, column=2, padx=5)

        self.btn_volver = ctk.CTkButton(self, text="Volver", command=self.destroy, width=120)
        self.btn_volver.pack(pady=(0, 12))

        self.after(150, lambda: self.iconbitmap(icono_logotipo))
        self._cargar_clientes()

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
                c["telefono"], c["email"], c["direccion"], c.get("iva", "")
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
        self.selected_cliente = None  # Reiniciamos la selección
        for ent in self.entries.values():
            ent.delete(0, tk.END)
        self.combobox_iva.set("")
        self.btn_agregar.configure(state="normal")
        self.btn_modificar.configure(state="disabled")
        self.btn_eliminar.configure(state="disabled")

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        cid = int(self.tree.item(sel[0], "values")[0])
        c = self.clientes_map[cid]
        # Actualizamos el formulario
        for k in self.entries:
            self.entries[k].delete(0, tk.END)
            self.entries[k].insert(0, c.get(k, ""))
        self.combobox_iva.set(c.get("iva", ""))
        self.cliente_actual_id = cid
        self.selected_cliente = c  # Guardamos el cliente seleccionado
        self.btn_agregar.configure(state="disabled")
        self.btn_modificar.configure(state="normal")
        self.btn_eliminar.configure(state="normal")

    def _agregar(self):
        if not (self.entries["nombre"].get().strip() and
                self.entries["apellido"].get().strip() and
                self.entries["cuil"].get().strip()):
            messagebox.showwarning("Atención", "Nombre, Apellido y CUIL son obligatorios.")
            return
        datos = {k: v.get().strip() for k, v in self.entries.items()}
        datos["iva"] = self.combobox_iva.get().strip()
        if self.cliente_manager.crear_cliente(datos):
            messagebox.showinfo("Éxito", "Cliente agregado.")
            self._cargar_clientes()
        else:
            messagebox.showerror("Error", "No se pudo agregar el cliente.")

    def _modificar(self):
        if self.cliente_actual_id is None:
            return
        datos = {k: v.get().strip() for k, v in self.entries.items()}
        datos["iva"] = self.combobox_iva.get().strip()
        if self.cliente_manager.actualizar_cliente(self.cliente_actual_id, datos):
            messagebox.showinfo("Éxito", "Cliente actualizado.")
            self._cargar_clientes()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el cliente.")

    def _eliminar(self):
        if self.cliente_actual_id is None:
            return
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
