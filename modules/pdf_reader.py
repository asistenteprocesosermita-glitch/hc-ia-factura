import fitz  # PyMuPDF

def extraer_texto_pdf(ruta_pdf):
    """
    Extrae texto de un PDF usando PyMuPDF.
    Si no puede leer alguna página, la salta sin romper el proceso.
    """

    texto_total = ""

    try:
        documento = fitz.open(ruta_pdf)

        for num_pagina in range(len(documento)):
            try:
                pagina = documento.load_page(num_pagina)
                texto_total += pagina.get_text("text") + "\n"
            except Exception:
                # Si una página falla, continúa con las demás
                continue

        documento.close()

    except Exception as e:
        return f"Error al leer PDF: {str(e)}"

    return texto_total
