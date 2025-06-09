# src/logica/generar_remito.py
import os
from datetime import datetime, date
from docxtpl import DocxTemplate
from docx.shared import Pt
from docx2pdf import convert
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
from datos.conexion_bd import ConexionBD

class RemitoGenerator:
    def __init__(self):
        # Se asume que la plantilla se encuentra en la carpeta del módulo
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.plantilla_path = os.path.join(BASE_DIR, "plantilla_remito.docx")
    
    def insert_table_in_doc(self, doc, carrito):
        """
        Busca el marcador %%tabla_placeholder_remito%% en la plantilla y lo 
        reemplaza por una tabla que muestra:
          - Producto
          - Cantidad
        """
        for tabla in doc.tables:
            for row in tabla.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        if "%%tabla_placeholder_remito%%" in para.text:
                            # Remover el párrafo que contiene el marcador
                            p_elem = para._element
                            cell._tc.remove(p_elem)
                            # Crear una tabla anidada de 2 columnas.
                            nested_table = cell.add_table(rows=1, cols=2)
                            nested_table.style = 'Table Grid'
                            hdr_cells = nested_table.rows[0].cells
                            hdr_cells[0].text = "Producto"
                            hdr_cells[1].text = "Cantidad"
                            # Formatear encabezados: fuente Helvetica, 10 pt, en negrita
                            for cell_hdr in nested_table.rows[0].cells:
                                for para_hdr in cell_hdr.paragraphs:
                                    for run in para_hdr.runs:
                                        run.font.name = 'Helvetica'
                                        run.font.size = Pt(10)
                                        run.font.bold = True
                            # Agregar una fila por cada producto vendido
                            for item in carrito:
                                row_cells = nested_table.add_row().cells
                                row_cells[0].text = item.get("nombre", "")
                                row_cells[1].text = str(item.get("cantidad", ""))
                            # Formatear los datos: fuente Helvetica, 10 pt sin negrita
                            for row_idx in range(1, len(nested_table.rows)):
                                for cell_data in nested_table.rows[row_idx].cells:
                                    for para_data in cell_data.paragraphs:
                                        for run in para_data.runs:
                                            run.font.name = 'Helvetica'
                                            run.font.size = Pt(10)
                                            run.font.bold = False
                            return

    def insertar_en_bd(self, cliente, carrito, fecha_venc):
        """
        Inserta los datos en las tablas Remito y RemitoDetalle.
        Para Remito se insertan los siguientes campos:
          - clienteID: se obtiene buscando en la tabla clientes por cuil.
          - cuit_cuil: cliente["cuit"]
          - ivaEstado: cliente["iva"]
          - fechaInicio: fecha actual (datetime.now().date())
          - vencimientoRemito: fecha de vencimiento (si se asigna) o NULL.
        Para RemitoDetalle se inserta una fila por cada producto del carrito:
          - remitoID
          - prodID
          - cantidad
        """
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("USE farmanaccio_db")
            
            # Obtener clienteID buscando por cuil
            cursor.execute("SELECT clienteId FROM clientes WHERE cuil=%s", (cliente.get("cuit"),))
            resultado = cursor.fetchone()
            if resultado:
                clienteID = resultado["clienteId"]
            else:
                clienteID = None
            
            sql_remito = """
                INSERT INTO Remito (clienteID, cuit_cuil, ivaEstado, fechaInicio, vencimientoRemito)
                VALUES (%s, %s, %s, %s, %s)
            """
            fecha_inicio = datetime.now().date()
            vencimientoRemito = fecha_venc.isoformat() if fecha_venc else None
            cursor.execute(
                sql_remito,
                (clienteID, cliente.get("cuit"), cliente.get("iva"), fecha_inicio.isoformat(), vencimientoRemito)
            )
            remitoID = cursor.lastrowid
            
            # Insertar en RemitoDetalle (sin loteID)
            sql_detalle = """
                INSERT INTO RemitoDetalle (remitoID, prodID, cantidad)
                VALUES (%s, %s, %s)
            """
            for item in carrito:
                cursor.execute(sql_detalle, (remitoID, item.get("prodId"), item.get("cantidad")))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            return remitoID
        except Exception as ex:
            try:
                conexion.rollback()
            except:
                pass
            messagebox.showerror("Error BD Remito", str(ex))
            return None

    def generar_remito_con_transaccion(self, parent, cliente, carrito, fecha_vencimiento=None):
        """
        Genera el remito usando la plantilla y asigna los siguientes datos:
          - Los campos IVA se completan con círculos (virtualmente).
          - RemitoID, fechaInicioRemito y horaInicioRemito se generan a partir de la hora actual para el documento.
          - fechaVencRemito se asigna según el valor seleccionado.
          - clienteNombre: concatenación de nombre y apellido.
          - clienteCUIT_CUIL y clienteDireccion se pasan.
          - %%tabla_placeholder_remito%% se reemplaza por una tabla que muestra Producto y Cantidad.
        Además, se inserta el remito y sus detalles en BD.
        """
        try:
            # Símbolos para vista en doc
            default_circle = "○"
            filled_circle = "●"
            client_iva = cliente.get("iva", "").lower()
            
            context = {
                "ivaExento": filled_circle if client_iva == "exento" else default_circle,
                "ivaMonotributo": filled_circle if client_iva == "monotributo" else default_circle,
                "ivaRespInsc": filled_circle if client_iva in ["resp. insc.", "responsable inscripto"] else default_circle,
                "ivaEventual": filled_circle if client_iva == "eventual" else default_circle,
                "ivaConsFinal": filled_circle if client_iva == "cons. final" else default_circle,
                "remitoID": f"REM-{int(datetime.now().timestamp())}",
                "fechaInicioRemito": datetime.now().date().isoformat(),
                "horaInicioRemito": datetime.now().time().strftime("%H:%M:%S"),
                "fechaVencRemito": fecha_vencimiento.isoformat() if fecha_vencimiento else "",
                "clienteNombre": f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}".strip(),
                "clienteCUIT_CUIL": cliente.get("cuit", ""),
                "clienteDireccion": cliente.get("direccion", ""),
                "%%tabla_placeholder_remito%%": "%%tabla_placeholder_remito%%"
            }
            
            # Insertamos en BD
            remitoID_bd = self.insertar_en_bd(cliente, carrito, fecha_vencimiento)
            if not remitoID_bd:
                return False
            
            doc = DocxTemplate(self.plantilla_path)
            doc.render(context)
            self.insert_table_in_doc(doc, carrito)
            
            ubicacion_docx = asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Archivos Word", "*.docx")],
                title="Guardar Remito"
            )
            if not ubicacion_docx:
                messagebox.showwarning("Cancelado", "La operación de guardado fue cancelada.", parent=parent)
                return False
            
            doc.save(ubicacion_docx)
            ubicacion_pdf = os.path.splitext(ubicacion_docx)[0] + ".pdf"
            convert(ubicacion_docx, ubicacion_pdf)
            os.remove(ubicacion_docx)
            messagebox.showinfo("Éxito", f"Remito guardado en {ubicacion_pdf}", parent=parent)
            return True
        except Exception as ex:
            messagebox.showerror("Error en Remito", str(ex), parent=parent)
            return False

    def generar_remito(self, parent, cliente, carrito, fecha_vencimiento=None):
        return self.generar_remito_con_transaccion(parent, cliente, carrito, fecha_vencimiento)


# Ejemplo de uso:
if __name__ == "__main__":
    from datetime import date
    dummy_cliente = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "direccion": "Av. Siempre Viva 123",
        "cuit": "20-12345678-9",
        "iva": "Monotributo"
    }
    dummy_carrito = [
        {"cantidad": 2, "nombre": "Producto A", "prodId": 1},
        {"cantidad": 1, "nombre": "Producto B", "prodId": 2}
    ]
    fecha_venc = date.today()
    RemitoGenerator().generar_remito(
        parent=None,
        cliente=dummy_cliente,
        carrito=dummy_carrito,
        fecha_vencimiento=fecha_venc
    )
