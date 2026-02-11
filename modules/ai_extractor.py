def extract_clinical_data(full_text):

    from modules.text_cleaner import split_text

    chunks = split_text(full_text, 7000)
    all_partial_results = []

    for chunk in chunks:

        prompt = f"""
Eres un auditor clínico experto en facturación hospitalaria.

Analiza este fragmento de historia clínica y EXTRAe SOLO información documentada explícitamente:

1. DATOS DEL PACIENTE (si aparecen)
2. FECHAS Y HORAS importantes (ingreso, egreso, traslados)
3. SERVICIOS donde estuvo:
   - Urgencias
   - Hospitalización
   - UCI
4. MEDICAMENTOS ADMINISTRADOS (NO formulados, solo aplicados)
5. PROCEDIMIENTOS REALIZADOS
6. LABORATORIOS E IMÁGENES
7. VALORACIONES DE ESPECIALISTAS
8. DISPOSITIVOS (catéter, ventilación, sondas)
9. EVENTOS CLÍNICOS relevantes

NO inventes información.
Si no aparece, no lo incluyas.

Texto:
{chunk}
"""

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        all_partial_results.append(response.choices[0].message.content)

    # 🔥 SEGUNDA IA: CONSOLIDAR TODO
    consolidation_prompt = f"""
Une toda esta información clínica sin repetir datos y organízala en este formato JSON:

{{
  "paciente": "",
  "ingreso": "",
  "egreso": "",
  "servicios": [],
  "dias_estancia_aprox": "",
  "medicamentos_administrados": [],
  "procedimientos_realizados": [],
  "laboratorios_imagenes": [],
  "valoraciones_especialistas": [],
  "dispositivos": [],
  "alertas_facturacion": []
}}

Información:
{all_partial_results}
"""

    final_response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": consolidation_prompt}],
        temperature=0
    )

    return final_response.choices[0].message.content
