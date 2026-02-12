import fitz  # PyMuPDF
import google.generativeai as genai
import streamlit as st
import base64
from config import AI_MODEL

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def extraer_texto_ocr(ruta_pdf):
    """
    Convierte cada página del PDF en imagen y usa Gemini Vision para extraer el texto.
    Funciona en Streamlit Cloud (no necesita Tesseract).
    """

    texto_total = ""
    modelo = genai.GenerativeModel(AI_MODEL)

    documento = fitz.open(ruta_pdf)

    for num_pagina in range(len(documento)):
        try:
            pagina = documento.load_page(num_pagina)
            pix = pagina.get_pixmap(dpi=200)

            # Convertir imagen a base64
            img_bytes = pix.tobytes("png")
            img_b64 = base64.b64encode(img_bytes).decode()

            prompt = "Extrae TODO el texto médico visible en esta imagen sin resumir."

            respuesta = modelo.generate_content([
                prompt,
                {
                    "mime_type": "image/png",
                    "data": img_b64
                }
            ])

            texto_total += respuesta.text + "\n"

        except Exception:
            continue

    documento.close()

    return texto_total
