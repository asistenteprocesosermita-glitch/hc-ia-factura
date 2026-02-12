import re


def clean_text(text):
    """
    Limpia texto extraído de PDF u OCR sin destruir estructura clínica.
    """

    if not text:
        return ""

    # Normalizar saltos de línea
    text = text.replace("\r", "\n")

    # Eliminar caracteres invisibles comunes en PDFs
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)

    # Quitar espacios múltiples dentro de líneas
    text = re.sub(r'[ \t]+', ' ', text)

    # Reducir saltos de línea excesivos (máx 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def dividir_texto(texto, tamaño_maximo):
    """
    Divide texto en bloques manejables para IA
    sin cortar palabras en la mitad.
    """

    bloques = []
    inicio = 0

    while inicio < len(texto):
        fin = inicio + tamaño_maximo

        # Evitar cortar en mitad de palabra
        if fin < len(texto):
            while fin > inicio and texto[fin] != " ":
                fin -= 1

        bloques.append(texto[inicio:fin].strip())
        inicio = fin

    return bloques
