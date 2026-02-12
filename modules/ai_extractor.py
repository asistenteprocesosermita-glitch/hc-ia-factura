import streamlit as st
import google.generativeai as genai
from config import AI_MODEL

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def analizar_historia_clinica(texto):

    modelo = genai.GenerativeModel(AI_MODEL)

    prompt = f"""
Eres auditor clínico experto en facturación hospitalaria.

Extrae SOLO información documentada explícitamente.

Devuelve JSON con:

- paciente
- ingreso
- egreso
- servicios
- medicamentos_administrados
- procedimientos_realizados
- laboratorios_imagenes
- valoraciones_especialistas
- dispositivos
- alertas_facturacion

Texto:
{texto}
"""

    response = modelo.generate_content(prompt)

    return response.text
