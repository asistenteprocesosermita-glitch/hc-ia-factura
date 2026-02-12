import sys
import os

# 🔥 ARREGLA IMPORTS EN STREAMLIT CLOUD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import streamlit as st
from modules.pdf_reader import extraer_texto_pdf
from modules.ocr_reader import extraer_texto_ocr
from modules.text_cleaner import limpiar_texto
from modules.ai_extractor import analizar_historia_clinica
from config import MAX_CHUNK_SIZE

st.set_page_config(page_title="HC IA Facturación", layout="wide")

st.title("📄 Analizador IA de Historia Clínica")
st.write("Carga una historia clínica para análisis médico y de facturación.")

# ---------------------------------
# SUBIDA DE ARCHIVO
# ---------------------------------
uploaded_file = st.file_uploader("Sube el PDF", type=["pdf"])

if uploaded_file:

    st.success("Archivo cargado correctamente")

    # Guardar temporalmente
    filepath = os.path.join(BASE_DIR, f"temp_{uploaded_file.name}")
    with open(filepath, "wb") as f:
        f.write(uploaded_file.read())

    # ---------------------------------
    # EXTRAER TEXTO DEL PDF
    # ---------------------------------
    with st.spinner("Extrayendo texto del documento..."):
        texto = extraer_texto_pdf(filepath)

    # Si el PDF es escaneado
    if len(texto.strip()) < 100:
        st.warning("Documento escaneado detectado. Aplicando OCR...")
        texto = extraer_texto_ocr(filepath)

    # ---------------------------------
    # LIMPIEZA DE TEXTO
    # ---------------------------------
    texto = limpiar_texto(texto)
    st.info(f"Texto extraído: {len(texto)} caracteres")

    # ---------------------------------
    # DIVIDIR EN BLOQUES
    # ---------------------------------
    def dividir_texto(texto, tamaño):
        return [texto[i:i+tamaño] for i in range(0, len(texto), tamaño)]

    bloques = dividir_texto(texto, MAX_CHUNK_SIZE)
    st.write(f"El documento se analizará en **{len(bloques)} bloques**")

    # ---------------------------------
    # BOTÓN DE ANÁLISIS IA
    # ---------------------------------
    if st.button("🔍 Analizar Historia Clínica"):

        resultados = []
        barra = st.progress(0)

        for i, bloque in enumerate(bloques):

            with st.spinner(f"Analizando bloque {i+1}/{len(bloques)}..."):
                resultado = analizar_historia_clinica(bloque)
                resultados.append(resultado)

            barra.progress((i + 1) / len(bloques))

        st.success("Análisis finalizado")

        # ---------------------------------
        # CONSOLIDAR RESULTADOS
        # ---------------------------------
        resultado_final = "\n\n".join(resultados)

        st.subheader("📊 Resultado del Análisis")
        st.text_area("Salida IA", resultado_final, height=500)
