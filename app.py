import streamlit as st
from datetime import date, datetime
from fpdf import FPDF

st.set_page_config(page_title="Evaluación Prematuros", layout="centered")

st.title("🩺 Evaluación de Crecimiento en Prematuros")

# Entrada de datos
st.subheader("📋 Datos del paciente")
fecha_nac = st.date_input("Fecha de nacimiento", format="YYYY-MM-DD")
eg = st.text_input("Edad gestacional al nacer (ej: 34+1)")
fecha_consulta = st.date_input("Fecha de consulta", format="YYYY-MM-DD")
peso = st.number_input("Peso actual (kg)", 0.0, 15.0, step=0.01)
talla = st.number_input("Talla actual (cm)", 0.0, 70.0, step=0.1)
pc = st.number_input("Perímetro cefálico (cm)", 0.0, 50.0, step=0.1)

# Cálculos automáticos
if eg and "+" in eg and st.button("Generar informe en PDF"):
    semanas, dias = map(int, eg.split("+"))
    edad_gestacional = semanas + dias / 7
    edad_cronologica = (fecha_consulta - fecha_nac).days / 7
    edad_postmenstrual = edad_gestacional + edad_cronologica
    edad_corregida = edad_cronologica - (40 - edad_gestacional)

    # Generar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Informe de Evaluación - Crecimiento en Prematuros", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Fecha de nacimiento: {fecha_nac}", ln=True)
    pdf.cell(200, 10, txt=f"Edad gestacional al nacer: {eg}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha de la consulta: {fecha_consulta}", ln=True)
    pdf.cell(200, 10, txt=f"Peso actual: {peso} kg", ln=True)
    pdf.cell(200, 10, txt=f"Talla actual: {talla} cm", ln=True)
    pdf.cell(200, 10, txt=f"Perímetro cefálico: {pc} cm", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Edad cronológica: {edad_cronologica:.1f} semanas", ln=True)
    pdf.cell(200, 10, txt=f"Edad corregida: {edad_corregida:.1f} semanas", ln=True)
    pdf.cell(200, 10, txt=f"Edad postmenstrual: {edad_postmenstrual:.1f} semanas", ln=True)

    st.success("✅ Informe generado correctamente")

    # Mostrar botón de descarga
    pdf_output = pdf.output(dest='S').encode('latin1')
    st.download_button("📥 Descargar informe PDF", pdf_output, file_name="informe_prematuro.pdf")
