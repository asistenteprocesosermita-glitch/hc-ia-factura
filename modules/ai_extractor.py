import streamlit as st
import google.generativeai as genai
import json
from config import AI_MODEL

# Configuración del modelo
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


def analizar_historia_clinica(texto):

    modelo = genai.GenerativeModel(
        AI_MODEL,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.9,
            "max_output_tokens": 2048
        }
    )

    prompt = f"""
Eres auditor clínico experto en facturación hospitalaria y auditoría para IPS.

INSTRUCCIONES:
- Extrae SOLO información explícitamente documentada.
- No inventes datos.
- Si un campo no aparece, devuelve null.
- Devuelve ÚNICAMENTE JSON válido.
- No agregues texto antes ni después del JSON.

Estructura:

{{
  "paciente": {{
    "nombre": "",
    "identificacion": "",
    "edad": "",
    "sexo": ""
  }},
  "ingreso": {{
    "fecha": "",
    "motivo": ""
  }},
  "egreso": {{
    "fecha": "",
    "diagnostico_principal": ""
  }},
  "servicios": [],
  "medicamentos_administrados": [],
  "procedimientos_realizados": [],
  "laboratorios_imagenes": [],
  "valoraciones_especialistas": [],
  "dispositivos": [],
  "alertas_facturacion": []
}}

Texto clínico:
\"\"\"{texto}\"\"\"
"""

    try:
        response = modelo.generate_content(prompt)

        contenido = response.text.strip()

        # Limpiar markdown si lo agrega
        if contenido.startswith("```"):
            contenido = contenido.replace("```json", "").replace("```", "").strip()

        datos = json.loads(contenido)

        return json.dumps(datos, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": "Error procesando con IA",
            "detalle": str(e)
        }, indent=2, ensure_ascii=False)
