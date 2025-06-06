import os

def generar_documento_txt(ruta_base: str, archivo_salida: str):
    """
    Recorre recursivamente la ruta base y, para cada archivo con extensión .py o .json,
    escribe su contenido en el archivo de salida, separando cada módulo con un separador.

    Args:
        ruta_base (str): Directorio base desde donde comenzar la búsqueda.
        archivo_salida (str): Nombre del archivo TXT a generar.
    """
    separador = "\n...-------------------...\n"
    with open(archivo_salida, "w", encoding="utf-8") as out_file:
        for root, dirs, files in os.walk(ruta_base):
            for archivo in files:
                if archivo.endswith(".py") or archivo.endswith(".json"):
                    ruta_archivo = os.path.join(root, archivo)
                    # Escribe el encabezado del archivo
                    out_file.write(separador)
                    out_file.write(f"Archivo: {ruta_archivo}\n")
                    out_file.write(separador)
                    try:
                        with open(ruta_archivo, "r", encoding="utf-8") as in_file:
                            contenido = in_file.read()
                        out_file.write(contenido)
                    except Exception as e:
                        out_file.write(f"Error al leer el archivo: {e}")
                    out_file.write("\n")
        out_file.write(separador)
    print(f"Documento generado en: {archivo_salida}")

if __name__ == "__main__":
    # Si el script se encuentra al mismo nivel que main.py,
    # establecemos la ruta base como el directorio actual.
    ruta_base = os.path.dirname(os.path.realpath(__file__))
    generar_documento_txt(ruta_base, "sistema_completo.txt")
