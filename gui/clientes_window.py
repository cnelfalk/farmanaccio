# src/gui/clientes_window.py
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, StringVar
from logica.gestor_clientes import ClienteManager
from gui.login import icono_logotipo
import tkinter.font as tkFont

class ClientesWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gestión de Clientes")
        self.resizable(False, False)

        self.cliente_manager = ClienteManager()
        self.cliente_actual_id = None
        self.selected_cliente = None
        self.clientes_map = {}

        # ─── FILTRO ACTIVO / ARCHIVADO ────────────────────
        self.frame_search = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_search.pack(fill="x", padx=10, pady=(10, 0))

        self.filter_var = tk.StringVar(value="Activos")
        self.filter_combobox = ctk.CTkComboBox(
            self.frame_search,
            values=["Activos", "Archivados"],
            variable=self.filter_var,
            width=120,
            command=self._cargar_por_filtro
        )
        self.filter_combobox.pack(side="left", padx=(0, 10))

        self.entry_search = ctk.CTkEntry(self.frame_search, placeholder_text="Buscar...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0,10))
        self.btn_search = ctk.CTkButton(self.frame_search, text="Buscar", width=100,
                                        command=self._buscar)
        self.btn_search.pack(side="left", padx=5)
        self.btn_reset = ctk.CTkButton(self.frame_search, text="Mostrar Todos", width=110,
                                       command=self._cargar_por_filtro)
        self.btn_reset.pack(side="left", padx=5)

        # ─── TREEVIEW ──────────────────────────────────────
        self.frame_tree_outer = ctk.CTkFrame(self, fg_color="#823F2A")
        self.frame_tree_outer.pack(fill="both", padx=10, pady=10)
        self.frame_tree = ctk.CTkFrame(self.frame_tree_outer, height=130)
        self.frame_tree.pack(fill="x", padx=10, pady=10)
        self.frame_tree.pack_propagate(False)

        cols = ("ID","Nombre","Apellido","CUIL","Teléfono","Email","Dirección","IVA")
        self.tree = ttk.Treeview(self.frame_tree, columns=cols, show="headings", height=5)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="w" if c!="ID" else "center")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        vs = ctk.CTkScrollbar(self.frame_tree, orientation="vertical", command=self.tree.yview)
        vs.grid(row=0, column=1, sticky="ns", pady=10)
        hs = ctk.CTkScrollbar(self.frame_tree, orientation="horizontal", command=self.tree.xview)
        hs.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.frame_tree.rowconfigure(0, weight=1)
        self.frame_tree.columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self._on_double_click)
        # placeholder para el mensaje “No hay…”
        self._lbl_no_data = None

        # ─── FORMULARIO ────────────────────────────────────
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(fill="x", padx=10, pady=(0,10))
        self.left = ctk.CTkFrame(self.frame_form, fg_color="#003D19")
        self.left.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5,0))
        self.right = ctk.CTkFrame(self.frame_form, fg_color="#003D19")
        self.right.grid(row=0, column=1, sticky="nsew", padx=5, pady=(5,0))
        self.frame_form.grid_columnconfigure(0, weight=1)
        self.frame_form.grid_columnconfigure(1, weight=1)

        self.entries = {}
        for i,(k,lbl) in enumerate([("nombre","Nombre"),("apellido","Apellido"),("telefono","Teléfono")]):
            ctk.CTkLabel(self.left, text=f"{lbl}:", width=100).grid(row=i,column=0,padx=5,pady=5)
            e=ctk.CTkEntry(self.left); e.grid(row=i,column=1,sticky="ew",padx=5,pady=5)
            self.entries[k]=e
        self.left.grid_columnconfigure(1,weight=1)

        for i,(k,lbl) in enumerate([("cuil","CUIT-CUIL"),("direccion","Dirección"),("email","E-mail")]):
            ctk.CTkLabel(self.right, text=f"{lbl}:", width=100).grid(row=i,column=0,padx=5,pady=5)
            e=ctk.CTkEntry(self.right); e.grid(row=i,column=1,sticky="ew",padx=5,pady=5)
            self.entries[k]=e
        self.right.grid_columnconfigure(1,weight=1)

        iva_frame = ctk.CTkFrame(self.frame_form, fg_color="#304C27")
        iva_frame.grid(row=1,column=0,columnspan=2,pady=5)
        ctk.CTkLabel(iva_frame, text="IVA:").pack(side="left",padx=5)
        opts = ["Exento","Monotributo","Resp. Insc.","Eventual","Cons. Final"]
        self.cmb_iva = ctk.CTkComboBox(iva_frame, values=opts, width=100, state="readonly")
        self.cmb_iva.set("")
        self.cmb_iva.pack(side="left",padx=5)

        self.frame_btns = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        self.frame_btns.grid(row=2,column=0,columnspan=2,pady=10)
        self.btn_agregar   = ctk.CTkButton(self.frame_btns,text="Agregar",  width=100,command=self._agregar)
        self.btn_modificar = ctk.CTkButton(self.frame_btns,text="Modificar",width=100,command=self._modificar)
        # renombramos aquí
        self.btn_eliminar  = ctk.CTkButton(self.frame_btns,text="Archivar",width=100,fg_color="red",command=self._archivar)
        self.btn_agregar.grid(  row=0,column=0,padx=5)
        self.btn_modificar.grid(row=0,column=1,padx=5)
        self.btn_eliminar.grid( row=0,column=2,padx=5)
        self.btn_restaurar = ctk.CTkButton(self.frame_btns, text="Restaurar", width=100,
                                   fg_color="green", command=self._restaurar_cliente)

        self.btn_volver = ctk.CTkButton(self,text="Volver",command=self.destroy,width=120)
        self.btn_volver.pack(pady=(0,12))

        self.after(150, lambda:self.iconbitmap(icono_logotipo))
        self._cargar_por_filtro()

    def _on_double_click(self, event):
        # Solo si estamos en la vista Archivados
        if self.filter_var.get() != "Archivados":
            return

        sel = self.tree.focus()
        if not sel:
            return

        # ID de la fila seleccionada
        cid = int(self.tree.item(sel, "values")[0])
        cliente = self.clientes_map.get(cid, {})

        razon = cliente.get("razonArchivado", "No hay razón registrada.")
        messagebox.showinfo(
            "Razón de archivado",
            razon,
            parent=self
        )

    def _clear_no_data(self):
        if self._lbl_no_data:
            self._lbl_no_data.destroy()
            self._lbl_no_data = None

    def _poblar(self, lista):
        self.tree.delete(*self.tree.get_children())
        self.clientes_map.clear()
        for c in lista:
            self.clientes_map[c["clienteID"]]=c
            vals = (c["clienteID"],c["nombre"],c["apellido"],c["cuil"],
                    c["telefono"],c["email"],c["direccion"],c.get("iva",""))
            self.tree.insert("", "end", values=vals)
        self._ajustar_id()

    def _restaurar_cliente(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un cliente para restaurar.", parent=self)
            return
        cid = int(self.tree.item(sel[0], "values")[0])
        if messagebox.askyesno("Confirmar", "¿Desea restaurar este cliente?", parent=self):
            if self.cliente_manager.restaurar_cliente(cid):
                messagebox.showinfo("Éxito", "Cliente restaurado.")
                self._cargar_por_filtro()
            else:
                messagebox.showerror("Error", "No se pudo restaurar el cliente.")


    def _cargar_por_filtro(self, *a):
        self._clear_no_data()
        estado = 1 if self.filter_var.get() == "Activos" else 0

        todos = self.cliente_manager.obtener_clientes()
        filt = [c for c in todos if c.get("activo", 1) == estado]

        # Si no hay datos archivados
        if estado == 0 and not filt:
            self.tree.delete(*self.tree.get_children())
            self._lbl_no_data = ctk.CTkLabel(
                self.frame_tree,
                text="No hay clientes archivados.",
                font=("Arial", 12),
                fg_color="#823F2A"
            )
            self._lbl_no_data.pack(expand=True, pady=20)
            return

        # Mostrar u ocultar botón Restaurar
        if estado == 0 and filt:
            self.btn_restaurar.grid(row=0, column=3, padx=5)
        else:
            self.btn_restaurar.grid_forget()

        # Poblamos el treeview
        self._poblar(filt)

    def _buscar(self):
        term = self.entry_search.get().strip().lower()
        if not term:
            return self._cargar_por_filtro()
        todos = self.cliente_manager.obtener_clientes()
        filt = [c for c in todos
                if term in c["nombre"].lower()
                or term in c["apellido"].lower()
                or term in c["cuil"].lower()]
        self._clear_no_data()
        self._poblar(filt)

    def _ajustar_id(self):
        if not self.clientes_map:
            self.tree.column("ID", width=50); return
        md = max(len(str(i)) for i in self.clientes_map)
        px = tkFont.Font().measure("0"*md)+16
        self.tree.column("ID", width=px)

    def _reset(self):
        self.cliente_actual_id=None
        self.selected_cliente=None
        for e in self.entries.values(): e.delete(0,tk.END)
        self.cmb_iva.set("")
        self.btn_agregar.configure(state="normal")
        self.btn_modificar.configure(state="disabled")
        self.btn_eliminar.configure(state="disabled")

    def _on_select(self,_):
        sel=self.tree.selection()
        if not sel: return
        cid=int(self.tree.item(sel[0],"values")[0])
        c=self.clientes_map[cid]
        for k in self.entries:
            e=self.entries[k]; e.delete(0,tk.END)
            e.insert(0,c.get(k,""))
        self.cmb_iva.set(c.get("iva",""))
        self.cliente_actual_id=cid
        self.selected_cliente=c
        self.btn_agregar.configure(state="disabled")
        if self.filter_var.get()=="Activos":
            self.btn_modificar.configure(state="normal")
            self.btn_eliminar.configure(state="normal")
        else:
            self.btn_modificar.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")

    def _agregar(self):
        if not (self.entries["nombre"].get().strip()
                and self.entries["apellido"].get().strip()
                and self.entries["cuil"].get().strip()):
            messagebox.showwarning("Atención","Nombre, Apellido y CUIL son obligatorios.")
            return
        datos={k:v.get().strip() for k,v in self.entries.items()}
        datos["iva"]=self.cmb_iva.get().strip()
        if self.cliente_manager.crear_cliente(datos):
            messagebox.showinfo("Éxito","Cliente agregado.")
            self._cargar_por_filtro()
        else:
            messagebox.showerror("Error","No se pudo agregar cliente.")

    def _modificar(self):
        if not self.cliente_actual_id: return
        datos={k:v.get().strip() for k,v in self.entries.items()}
        datos["iva"]=self.cmb_iva.get().strip()
        if self.cliente_manager.actualizar_cliente(self.cliente_actual_id, datos):
            messagebox.showinfo("Éxito","Cliente actualizado.")
            self._cargar_por_filtro()
        else:
            messagebox.showerror("Error","No se pudo actualizar cliente.")

    def _archivar(self):
        if not self.cliente_actual_id:
            return

        from utils.utilidades import CTkPromptArchivado
        prompt = CTkPromptArchivado(self, titulo="Archivar cliente", mensaje="Motivo de archivado:")
        razon = prompt.resultado
        if razon is None:
            return

        if self.cliente_manager.eliminar_cliente(self.cliente_actual_id, razon.strip()):
            messagebox.showinfo("Éxito", "Cliente archivado.")
            self._cargar_por_filtro()
        else:
            messagebox.showerror("Error", "No se pudo archivar cliente.")


if __name__=="__main__":
    root=tk.Tk(); root.withdraw()
    ClientesWindow(root).mainloop()
