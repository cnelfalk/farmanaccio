# src/login/generar_factura.py
import os
from datetime import datetime
from datos.conexion_bd import ConexionBD
from docxtpl import DocxTemplate
from mysql.connector import Error
from docx2pdf import convert
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
from docx.shared import Pt

class FacturaGenerator:
    """
    Encapsula la generación de la factura:
      - Recupera los datos de la última factura y sus detalles.
      - Inserta dinámicamente una tabla en la plantilla (en el lugar del marcador).
      - Renderiza el documento DOCX y lo convierte a PDF.
    """
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # Ubicación de la plantilla
        self.plantilla_document = os.path.join(BASE_DIR, "plantilla_factura.docx")

    def obtener_factura_y_detalles(self):
        """
        Recupera la última factura ingresada en la base de datos y sus detalles.
        Retorna una tupla (datos_factura, detalles) donde:
          - datos_factura es un diccionario con: facturaId, fechaEmision, horaEmision, total_neto, total_bruto, descuento.
          - detalles es una lista de diccionarios donde cada elemento contiene: prodId, nombre, cantidad, precioUnitario y subtotal.
        """
        datos_factura = None
        detalles = []
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            if conexion:
                cursor.execute("USE ventas_db")
                cursor.execute("""
                    SELECT facturaId AS facturaId,
                           fechaEmision,
                           horaEmision,
                           total_neto,
                           total_bruto,
                           descuento
                    FROM facturas
                    ORDER BY facturaId DESC
                    LIMIT 1
                """)
                datos_factura = cursor.fetchone()
                if datos_factura:
                    factura_id = datos_factura["facturaId"]
                    cursor.execute("""
                        SELECT fd.prodId,
                               p.nombre,
                               fd.cantidad,
                               fd.precioUnitario
                        FROM factura_detalles fd
                        JOIN productos p ON fd.prodId = p.prodId
                        WHERE fd.facturaID = %s
                    """, (factura_id,))
                    detalles = cursor.fetchall()
                    for detalle in detalles:
                        detalle["subtotal"] = detalle["cantidad"] * detalle["precioUnitario"]
        except Error as e:
            print("Error al obtener la factura:", e)
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()
        return datos_factura, detalles

    def insert_table_in_doc(self, doc, detalles):
        """
        Recorre las tablas del documento buscando el marcador "%%tabla_placeholder%%". Cuando lo encuentra,
        borra el párrafo que lo contiene e inserta una tabla anidada formateada con 4 columnas:
           Cantidad, Producto, Precio Unitario y Sub-total.
        Se establece:
          - Encabezados en fuente HelveticaNeueLT Pro 35 Th, 10 pt, en negrita.
          - Datos en la misma fuente, 10 pt, sin negrita.
        """
        # Itera sobre cada tabla del documento
        for tabla in doc.tables:
            for row in tabla.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        if "%%tabla_placeholder%%" in para.text:
                            # Remover el párrafo que contiene el marcador
                            p_elem = para._element
                            cell._tc.remove(p_elem)
                            
                            # Agregar una tabla anidada en la celda
                            nested_table = cell.add_table(rows=1, cols=4)
                            nested_table.style = 'Table Grid'
                            hdr_cells = nested_table.rows[0].cells
                            hdr_cells[0].text = "Cantidad"
                            hdr_cells[1].text = "Producto"
                            hdr_cells[2].text = "Precio Unitario"
                            hdr_cells[3].text = "Sub-total"
                            
                            # Formatea los encabezados: 10 pt, en negrita.
                            for cell_hdr in nested_table.rows[0].cells:
                                for para_hdr in cell_hdr.paragraphs:
                                    for run in para_hdr.runs:
                                        run.font.name = 'HelveticaNeueLT Pro 35 Th'
                                        run.font.size = Pt(10)
                                        run.font.bold = True
                            
                            # Agrega una fila por cada producto en 'detalles'
                            for item in detalles:
                                row_cells = nested_table.add_row().cells
                                row_cells[0].text = str(item["cantidad"])
                                row_cells[1].text = item["nombre"]
                                row_cells[2].text = f"{item['precioUnitario']:.2f}"
                                row_cells[3].text = f"{item['subtotal']:.2f}"
                            
                            # Formatea los datos: 10 pt, sin negrita.
                            for row_idx in range(1, len(nested_table.rows)):
                                for cell_data in nested_table.rows[row_idx].cells:
                                    for para_data in cell_data.paragraphs:
                                        for run in para_data.runs:
                                            run.font.name = 'HelveticaNeueLT Pro 35 Th'
                                            run.font.size = Pt(10)
                                            run.font.bold = False
                            return  # Una vez reemplazado, se sale del método

    def generar_factura(self, parent):
        """
        Genera la factura en formato DOCX a partir de la plantilla, inserta la tabla
        de detalles en el marcador y la convierte a PDF. Si no se obtiene la factura
        de la base de datos, muestra un error.
        """
        datos_factura, detalles = self.obtener_factura_y_detalles()
        if not datos_factura:
            messagebox.showerror("Error de Generación", "No se pudo generar la factura.", parent=parent)
            return
        try:
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
            
            # Se inserta la tabla en el documento, reemplazando el marcador.
            self.insert_table_in_doc(doc, detalles)
            
            ubicacion_docx = asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word files", "*.docx")],
                title="Guarde la factura"
            )
            if ubicacion_docx:
                doc.save(ubicacion_docx)
                ubicacion_pdf = os.path.splitext(ubicacion_docx)[0] + ".pdf"
                convert(ubicacion_docx, ubicacion_pdf)
                os.remove(ubicacion_docx)
                messagebox.showinfo("Éxito", f"Factura guardada en {ubicacion_pdf}", parent=parent)
            else:
                messagebox.showwarning("Cancelación", "La operación de guardado fue cancelada.", parent=parent)
        except Error as e:
            print("Error durante la generación de la factura:", e)
        except Exception as ex:
            print("Error:", ex)

# Ejemplo de uso:
if __name__ == "__main__":
    # Para pruebas unitarias, se puede simular una llamada sin UI:
    fg = FacturaGenerator()
    # Aquí 'parent' se podría reemplazar por None o por un contenedor simulado
    fg.generar_factura(parent=None)