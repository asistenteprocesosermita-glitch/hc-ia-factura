import streamlit as st
import fitz  # PyMuPDF
from modules.text_cleaner import clean_text
from modules.ai_extractor import extract_clinical_data

st.title("📄 Analizador IA de Historia Clínica")

uploaded_file = st.file_uploader("Subir Historia Clínica", type=["pdf"])

if uploaded_file:

    st.success("Archivo cargado correctamente.")

    # 📄 LEER PDF DIRECTAMENTE EN MEMORIA
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text()

    cleaned_text = clean_text(text)

    st.subheader("📑 Texto detectado")
    st.text_area("Texto", cleaned_text[:3000], height=250)

    st.subheader("🤖 Análisis con IA")

    if st.button("Analizar Historia Clínica"):
        with st.spinner("La IA está analizando..."):
            result = extract_clinical_data(cleaned_text)

        st.subheader("🧠 Resultado")
        st.write(result)
