import fitz  # PyMuPDF


def extraer_texto_pdf(ruta_pdf):
    """
    Extrae texto de un PDF usando PyMuPDF.
    - Si una página falla, la omite.
    - Elimina páginas completamente vacías.
    - Devuelve texto limpio.
    """

    texto_total = ""

    try:
        with fitz.open(ruta_pdf) as documento:

            for num_pagina in range(len(documento)):
                try:
                    pagina = documento.load_page(num_pagina)
                    texto = pagina.get_text("text")

                    # Solo agregar si realmente tiene contenido
                    if texto and texto.strip():
                        texto_total += texto.strip() + "\n\n"

                except Exception:
                    # Continúa si una página falla
                    continue

    except Exception as e:
        return f"Error al leer PDF: {str(e)}"

    return texto_total.strip()
