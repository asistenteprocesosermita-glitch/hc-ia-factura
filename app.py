import streamlit as st
from modules.pdf_reader import extraer_texto_pdf
from modules.ocr_reader import extraer_texto_ocr
from modules.text_cleaner import limpiar_texto
from modules.ai_extractor import analizar_historia_clinica
from config import MAX_CHUNK_SIZE

st.set_page_config(page_title="HC IA Facturación", layout="wide")

st.title("📄 Analizador de Historia Clínica - Facturación")

st.write("Sube una historia clínica en PDF para analizarla con IA.")

# ---------------------------
# SUBIDA DE ARCHIVO
# ---------------------------

uploaded_file = st.file_uploader("Cargar PDF", type=["pdf"])

if uploaded_file:

    st.success("Documento cargado correctamente")

    # Guardar temporalmente
    filepath = f"temp_{uploaded_file.name}"
    with open(filepath, "wb") as f:
        f.write(uploaded_file.read())

    # ---------------------------
    # EXTRAER TEXTO
    # ---------------------------

    with st.spinner("Extrayendo texto del PDF..."):
        texto = extraer_texto_pdf(filepath)

    # Si el PDF no tiene texto (escaneado)
    if len(texto.strip()) < 100:
        st.warning("PDF escaneado detectado. Aplicando OCR...")
        texto = extraer_texto_ocr(filepath)

    # ---------------------------
    # LIMPIAR TEXTO
    # ---------------------------

    texto = limpiar_texto(texto)

    st.info(f"Longitud total del texto: {len(texto)} caracteres")

    # ---------------------------
    # DIVIDIR EN BLOQUES GRANDES
    # ---------------------------

    def dividir_en_bloques(texto, tamaño):
        return [texto[i:i+tamaño] for i in range(0, len(texto), tamaño)]

    bloques = dividir_en_bloques(texto, MAX_CHUNK_SIZE)

    st.write(f"El documento será procesado en {len(bloques)} bloque(s)")

    # ---------------------------
    # BOTÓN DE ANÁLISIS
    # ---------------------------

    if st.button("🔍 Analizar Historia Clínica"):

        resultados_totales = []

        progress_bar = st.progress(0)

        for i, bloque in enumerate(bloques):

            with st.spinner(f"Analizando bloque {i+1} de {len(bloques)}..."):
                resultado = analizar_historia_clinica(bloque)
                resultados_totales.append(resultado)

            progress_bar.progress((i + 1) / len(bloques))

        st.success("Análisis completado")

        # ---------------------------
        # MOSTRAR RESULTADO FINAL
        # ---------------------------

        st.subheader("📊 Resultado Consolidado")

        resultado_final = "\n\n".join(resultados_totales)

        st.text_area(
            "Resultado IA",
            resultado_final,
            height=500
        )
