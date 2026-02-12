import fitz
import google.generativeai as genai
import streamlit as st
import base64
from config import AI_MODEL

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def extraer_texto_ocr(ruta_pdf):

    texto_total = ""
    modelo = genai.GenerativeModel(AI_MODEL)
    documento = fitz.open(ruta_pdf)

    for i in range(len(documento)):
        pagina = documento.load_page(i)
        pix = pagina.get_pixmap(dpi=200)

        img_bytes = pix.tobytes("png")
        img_b64 = base64.b64encode(img_bytes).decode()

        respuesta = modelo.generate_content([
            "Extrae TODO el texto médico visible.",
            {"mime_type": "image/png", "data": img_b64}
        ])

        texto_total += respuesta.text + "\n"

    documento.close()
    return texto_total
