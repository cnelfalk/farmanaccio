# src/logica/generar_factura.py

import os
from datetime import datetime
from docxtpl import DocxTemplate
from docx2pdf import convert
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
from docx.shared import Pt

class FacturaGenerator:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # Ruta de la plantilla DOCX
        self.plantilla_document = os.path.join(BASE_DIR, "plantilla_factura.docx")

    def obtener_factura_y_detalles(self, cursor, factura_id):
        """
        Recupera la factura con ID factura_id y sus detalles usando el cursor
        de la transacción actual.
        """
        datos_factura = None
        detalles = []
        cursor.execute("""
            SELECT facturaId, fechaEmision, horaEmision, total_neto, total_bruto, descuento
            FROM facturas
            WHERE facturaId = %s
            """, (factura_id,))
        datos_factura = cursor.fetchone()
        if datos_factura:
            cursor.execute("""
                SELECT fd.prodId, p.nombre, fd.cantidad, fd.precioUnitario
                FROM factura_detalles fd
                JOIN productos p ON fd.prodId = p.prodId
                WHERE fd.facturaID = %s
            """, (factura_id,))
            detalles = cursor.fetchall()
            for detalle in detalles:
                detalle["subtotal"] = detalle["cantidad"] * detalle["precioUnitario"]
        return datos_factura, detalles

    def insert_table_in_doc(self, doc, detalles):
        """
        Busca el marcador %%tabla_placeholder%% en la plantilla y lo reemplaza
        por una tabla anidada con las columnas: Cantidad, Producto, Precio Unitario y Sub-total.
        """
        for tabla in doc.tables:
            for row in tabla.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        if "%%tabla_placeholder%%" in para.text:
                            # Remover párrafo que contiene el marcador
                            p_elem = para._element
                            cell._tc.remove(p_elem)
                            # Agregar tabla anidada en la celda
                            nested_table = cell.add_table(rows=1, cols=4)
                            nested_table.style = 'Table Grid'
                            hdr_cells = nested_table.rows[0].cells
                            hdr_cells[0].text = "Cantidad"
                            hdr_cells[1].text = "Producto"
                            hdr_cells[2].text = "Precio Unitario"
                            hdr_cells[3].text = "Sub-total"
                            # Formatear encabezados: 10 pt y en negrita
                            for cell_hdr in nested_table.rows[0].cells:
                                for para_hdr in cell_hdr.paragraphs:
                                    for run in para_hdr.runs:
                                        run.font.name = 'HelveticaNeueLT Pro 35 Th'
                                        run.font.size = Pt(10)
                                        run.font.bold = True
                            # Agregar una fila por cada producto
                            for item in detalles:
                                row_cells = nested_table.add_row().cells
                                row_cells[0].text = str(item["cantidad"])
                                row_cells[1].text = item["nombre"]
                                row_cells[2].text = f"{item['precioUnitario']:.2f}"
                                row_cells[3].text = f"{item['subtotal']:.2f}"
                            # Formatear datos: 10 pt sin negrita
                            for row_idx in range(1, len(nested_table.rows)):
                                for cell_data in nested_table.rows[row_idx].cells:
                                    for para_data in cell_data.paragraphs:
                                        for run in para_data.runs:
                                            run.font.name = 'HelveticaNeueLT Pro 35 Th'
                                            run.font.size = Pt(10)
                                            run.font.bold = False
                            return

    def generar_factura_con_transaccion(self, parent, conexion, factura_id):
        """
        Genera la factura utilizando la conexión activa (la misma de la transacción)
        y solicita al usuario la ubicación para guardar el archivo. Si el usuario cancela,
        se retorna False para que se ejecute un rollback.
        """
        try:
            cursor = conexion.cursor(dictionary=True)
            datos_factura, detalles = self.obtener_factura_y_detalles(cursor, factura_id)
            if not datos_factura:
                messagebox.showerror("Error de Generación", "No se pudo generar la factura.", parent=parent)
                return False
            
            context = {
                "facturaId": datos_factura["facturaId"],
                "fecha": datos_factura["fechaEmision"],
                "hora": datos_factura["horaEmision"],
                "descuento": f"{int(datos_factura['descuento'])}%",
                "total_neto": datos_factura["total_neto"],
                "total_bruto": datos_factura["total_bruto"],
                "tabla_placeholder": "%%tabla_placeholder%%"
            }
            
            doc = DocxTemplate(self.plantilla_document)
            doc.render(context)
            self.insert_table_in_doc(doc, detalles)
            
            ubicacion_docx = asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word files", "*.docx")],
                title="Guarde la factura"
            )
            if not ubicacion_docx:
                messagebox.showwarning("Cancelación", "La operación de guardado fue cancelada.", parent=parent)
                return False
            
            doc.save(ubicacion_docx)
            ubicacion_pdf = os.path.splitext(ubicacion_docx)[0] + ".pdf"
            convert(ubicacion_docx, ubicacion_pdf)
            os.remove(ubicacion_docx)
            messagebox.showinfo("Éxito", f"Factura guardada en {ubicacion_pdf}", parent=parent)
            return True
        except Exception as ex:
            messagebox.showerror("Error", str(ex), parent=parent)
            return False
        finally:
            cursor.close()

    # Método wrapper que redirige a la versión transaccional.
    def generar_factura(self, parent, conexion, factura_id):
        return self.generar_factura_con_transaccion(parent, conexion, factura_id)
