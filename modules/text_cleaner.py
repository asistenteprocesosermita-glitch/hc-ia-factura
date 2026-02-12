import re

def clean_text(raw_text: str) -> str:
    """
    Limpia el texto extraído: elimina saltos de línea excesivos,
    normaliza espacios, corrige caracteres mal interpretados.
    """
    # Reemplazar múltiples saltos de línea por uno solo
    text = re.sub(r'\n\s*\n', '\n', raw_text)
    # Eliminar espacios múltiples
    text = re.sub(r'[ \t]+', ' ', text)
    # Corregir OCR común: '|' por 'I', '0' por 'O' en contexto, etc.
    text = text.replace('|', 'I').replace('0 ', 'O ')
    return text.strip()
