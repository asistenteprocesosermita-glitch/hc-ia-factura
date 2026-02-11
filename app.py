import streamlit as st
import os
from modules.pdf_reader import extract_text_from_pdf
from modules.ocr_reader import extract_text_with_ocr
from modules.text_cleaner import clean_text

UPLOAD_FOLDER = "data/uploads"

st.set_page_config(page_title="Analizador de Historia Clínica", layout="wide")

st.title("📄 Analizador IA de Historia Clínica")
st.write("Sube la HC en PDF para analizarla automáticamente.")

uploaded_file = st.file_uploader("Cargar Historia Clínica", type=["pdf"])

if uploaded_file:
    filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Archivo cargado correctamente.")

    st.subheader("🔍 Extrayendo texto...")

    text = extract_text_from_pdf(filepath)

    if len(text.strip()) < 100:  # probablemente es escaneado
        st.warning("PDF escaneado detectado. Aplicando OCR...")
        text = extract_text_with_ocr(filepath)

    cleaned_text = clean_text(text)

    st.subheader("📑 Texto detectado (resumen)")
    st.text_area("Texto", cleaned_text[:5000], height=300)

    st.subheader("🤖 (Próximo paso) Análisis con IA")
    st.info("Aquí conectaremos el modelo para extraer datos clínicos.")
