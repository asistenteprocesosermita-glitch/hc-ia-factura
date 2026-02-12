import fitz
import google.generativeai as genai
import streamlit as st
import base64
from config import AI_MODEL

# Configurar API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


def extraer_texto_ocr(ruta_pdf):

    texto_total = ""

    modelo = genai.GenerativeModel(
        model_name=AI_MODEL,
        generation_config={
            "temperature": 0.0,   # OCR debe ser totalmente preciso
            "max_output_tokens": 2048
        }
    )

    try:
        documento = fitz.open(ruta_pdf)

        for i in range(len(documento)):

            try:
                pagina = documento.load_page(i)
                pix = pagina.get_pixmap(dpi=200)

                img_bytes = pix.tobytes("png")
                img_b64 = base64.b64encode(img_bytes).decode()

                prompt = """
Extrae TODO el texto visible en esta imagen médica.
- No resumas.
- No interpretes.
- No estructures.
- Devuelve exactamente el texto tal como aparece.
"""

                respuesta = modelo.generate_content([
                    prompt,
                    {"mime_type": "image/png", "data": img_b64}
                ])

                if respuesta.text:
                    texto_total += respuesta.text.strip() + "\n\n"

            except Exception as error_pagina:
                texto_total += f"\n[Error procesando página {i+1}: {str(error_pagina)}]\n"

        documento.close()

    except Exception as e:
        return f"Error abriendo PDF: {str(e)}"

    return texto_total.strip()
