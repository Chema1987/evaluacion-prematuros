import streamlit as st
from datetime import date
from fpdf import FPDF
import matplotlib.pyplot as plt
import io

# --- Funciones auxiliares ---

def calcular_percentil(valor, media, desviacion):
    if valor < media - 2 * desviacion:
        return "<P3"
    elif valor > media + 2 * desviacion:
        return ">P97"
    else:
        return f"P{int(50 + ((valor - media)/desviacion)*10):.0f}"

def generar_grafico(parametro, edad, valor):
    edades = list(range(0, 25))
    p3 = [media - 2 for media in range(30, 55)]
    p50 = [media for media in range(30, 55)]
    p97 = [media + 2 for media in range(30, 55)]

    plt.figure()
    plt.plot(edades, p3, label="P3", linestyle=":")
    plt.plot(edades, p50, label="P50", linestyle="--")
    plt.plot(edades, p97, label="P97", linestyle=":")
    plt.scatter([edad], [valor], color="red", label="Paciente")
    plt.xlabel("Edad corregida (meses)")
    plt.ylabel(parametro)
    plt.title(f"{parametro} - Curvas OMS (simulado)")
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf

# --- Interfaz Streamlit ---

st.set_page_config(page_title="Evaluación Prematuros", layout="centered")
st.title("🩺 Evaluación de Crecimiento en Prematuros")

with st.form("formulario"):
    col1, col2 = st.columns(2)
    with col1:
        fecha_nac = st.date_input("📅 Fecha de nacimiento")
        eg = st.text_input("🗓 Edad gestacional (ej. 34+1)")
        sexo = st.selectbox("👶 Sexo", ["Niña", "Niño"])
    with col2:
        fecha_consulta = st.date_input("📅 Fecha de consulta")
        peso = st.number_input("⚖️ Peso (kg)", 0.0, 10.0, step=0.01)
        talla = st.number_input("📏 Talla (cm)", 30.0, 60.0, step=0.1)
        pc = st.number_input("🧠 Perímetro cefálico (cm)", 20.0, 50.0, step=0.1)
    enviar = st.form_submit_button("📄 Generar informe")

if enviar and "+" in eg:
    semanas, dias = map(int, eg.split("+"))
    eg_total = semanas + dias / 7
    edad_cronologica = (fecha_consulta - fecha_nac).days / 7
    edad_postmenstrual = eg_total + edad_cronologica
    edad_corregida = edad_cronologica - (40 - eg_total)

    peso_pct = calcular_percentil(peso, 4.5, 1.0)
    talla_pct = calcular_percentil(talla, 54, 2.0)
    pc_pct = calcular_percentil(pc, 37, 1.5)

    st.subheader("📊 Resultados")
    st.write(f"Edad corregida: {edad_corregida:.1f} semanas")
    st.write(f"Edad postmenstrual: {edad_postmenstrual:.1f} semanas")
    st.write(f"Peso: {peso} kg -> {peso_pct}")
    st.write(f"Talla: {talla} cm -> {talla_pct}")
    st.write(f"Perímetro cefálico: {pc} cm -> {pc_pct}")

    st.subheader("📈 Gráficas")
    graficos = {}
    for parametro, valor in zip(["Peso (kg)", "Talla (cm)", "Perímetro cefálico (cm)"], [peso, talla, pc]):
        grafico = generar_grafico(parametro, edad_corregida/4.3, valor)
        graficos[parametro] = grafico
        st.image(grafico, caption=parametro)

    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Evaluacion - Prematuros", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Sexo: {sexo}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha de nacimiento: {fecha_nac.strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(200, 10, txt=f"Edad gestacional: {eg}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha de consulta: {fecha_consulta.strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Edad corregida: {edad_corregida:.1f} semanas", ln=True)
    pdf.cell(200, 10, txt=f"Edad postmenstrual: {edad_postmenstrual:.1f} semanas", ln=True)
    pdf.cell(200, 10, txt=f"Peso: {peso} kg -> {peso_pct}", ln=True)
    pdf.cell(200, 10, txt=f"Talla: {talla} cm -> {talla_pct}", ln=True)
    pdf.cell(200, 10, txt=f"Perímetro cefálico: {pc} cm -> {pc_pct}", ln=True)

    for parametro, grafico in graficos.items():
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=parametro, ln=True)
        img_bytes = grafico.getvalue()
        with open("grafico_temp.png", "wb") as f:
            f.write(img_bytes)
        pdf.image("grafico_temp.png", x=10, y=30, w=180)

    # Descargar PDF sin codificación especial
    pdf_output = pdf.output(dest='S').encode("latin-1", errors="ignore")
    st.download_button("📥 Descargar informe PDF", pdf_output, file_name="informe_prematuro.pdf")
