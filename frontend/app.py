import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Risco Cardíaco",
    page_icon="🫀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS customizado ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Fundo geral */
.stApp {
    background-color: #F7F4EF;
}

/* Cabeçalho hero */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: #1a1a1a;
    margin-bottom: 0.3rem;
    line-height: 1.15;
}
.hero p {
    font-size: 1rem;
    color: #666;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Seções do formulário */
.section-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #999;
    margin: 2rem 0 0.8rem;
    border-bottom: 1px solid #E5E0D8;
    padding-bottom: 0.4rem;
}

/* Card de resultado */
.result-card {
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin: 1.5rem 0;
}
.result-card.baixo     { background: #E8F7F1; border: 1.5px solid #1D9E75; }
.result-card.moderado  { background: #FEF6E7; border: 1.5px solid #EF9F27; }
.result-card.alto      { background: #FEF0E6; border: 1.5px solid #E07020; }
.result-card.muito_alto{ background: #FAECEC; border: 1.5px solid #D85A30; }

.result-pct {
    font-family: 'DM Serif Display', serif;
    font-size: 4.5rem;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.result-label {
    font-size: 1.1rem;
    font-weight: 500;
    margin-bottom: 0.8rem;
}
.result-aviso {
    font-size: 0.78rem;
    color: #888;
    max-width: 380px;
    margin: 1rem auto 0;
    line-height: 1.5;
}

/* Barra de progresso de risco */
.risk-bar-wrap {
    background: #E5E0D8;
    border-radius: 99px;
    height: 8px;
    margin: 0.8rem auto;
    max-width: 320px;
    overflow: hidden;
}
.risk-bar-fill {
    height: 8px;
    border-radius: 99px;
    transition: width 0.8s ease;
}

/* Botão principal */
div[data-testid="stButton"] > button {
    background-color: #1a1a1a !important;
    color: #F7F4EF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 2.5rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    margin-top: 1rem !important;
    transition: opacity 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    opacity: 0.85 !important;
}

/* Ocultar header/footer padrão do streamlit */
#MainMenu, footer, header { visibility: hidden; }

/* Divisor */
hr { border: none; border-top: 1px solid #E5E0D8; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
AGE_LABELS = {
    1: "18–24 anos", 2: "25–29 anos", 3: "30–34 anos", 4: "35–39 anos",
    5: "40–44 anos", 6: "45–49 anos", 7: "50–54 anos", 8: "55–59 anos",
    9: "60–64 anos", 10: "65–69 anos", 11: "70–74 anos",
    12: "75–79 anos", 13: "80 anos ou mais",
}
EDU_LABELS = {
    1: "Nunca estudou", 2: "Ensino Fundamental I", 3: "Ensino Fundamental II",
    4: "Ensino Médio incompleto", 5: "Ensino Médio completo", 6: "Superior completo",
}
INCOME_LABELS = {
    1: "Muito baixa", 2: "Baixa", 3: "Baixa-média",
    4: "Média", 5: "Média-alta", 6: "Alta", 7: "Muito alta", 8: "Acima de R$15k/mês",
}
DIABETES_LABELS = {0: "Não tenho", 1: "Pré-diabetes", 2: "Diabetes confirmado"}
GENHLTH_LABELS  = {1: "Excelente", 2: "Muito boa", 3: "Boa", 4: "Regular", 5: "Ruim"}


def calcular_bmi(peso: float, altura_cm: float) -> tuple[float, int]:
    h = altura_cm / 100
    bmi = round(peso / h ** 2, 1)
    cat = 0 if bmi < 18.5 else 1 if bmi < 25 else 2 if bmi < 30 else 3
    return bmi, cat


def cor_nivel(label: str) -> str:
    return {"Baixo": "#1D9E75", "Moderado": "#EF9F27",
            "Alto": "#E07020", "Muito Alto": "#D85A30"}.get(label, "#888")


def css_class_nivel(label: str) -> str:
    return {"Baixo": "baixo", "Moderado": "moderado",
            "Alto": "alto", "Muito Alto": "muito_alto"}.get(label, "baixo")


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🫀 Avaliação de<br><em>Risco Cardíaco</em></h1>
    <p>Responda algumas perguntas simples e descubra sua estimativa de risco.
       Nenhum exame necessário.</p>
</div>
""", unsafe_allow_html=True)

# ── Formulário ────────────────────────────────────────────────────────────────
with st.form("formulario_risco"):

    # SEÇÃO 1 — Dados pessoais
    st.markdown('<div class="section-label">Dados pessoais</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        peso = st.number_input("Peso (kg)", min_value=30.0, max_value=250.0,
                                value=70.0, step=0.5)
    with col2:
        altura = st.number_input("Altura (cm)", min_value=100.0, max_value=230.0,
                                  value=170.0, step=0.5)
    with col3:
        sexo = st.selectbox("Sexo", options=[0, 1],
                             format_func=lambda x: "Feminino" if x == 0 else "Masculino")

    col4, col5 = st.columns(2)
    with col4:
        age_val = st.selectbox("Faixa etária", options=list(AGE_LABELS.keys()),
                                format_func=lambda x: AGE_LABELS[x], index=5)
    with col5:
        edu_val = st.selectbox("Escolaridade", options=list(EDU_LABELS.keys()),
                                format_func=lambda x: EDU_LABELS[x], index=4)

    income_val = st.selectbox("Faixa de renda", options=list(INCOME_LABELS.keys()),
                               format_func=lambda x: INCOME_LABELS[x], index=3)

    # SEÇÃO 2 — Histórico de saúde
    st.markdown('<div class="section-label">Histórico de saúde</div>', unsafe_allow_html=True)
    col6, col7 = st.columns(2)
    with col6:
        pressao_alta  = st.checkbox("Tenho pressão alta diagnosticada")
        colesterol    = st.checkbox("Tenho colesterol alto diagnosticado")
        check_col     = st.checkbox("Fiz check de colesterol nos últimos 5 anos")
        avc           = st.checkbox("Já tive AVC")
    with col7:
        dif_caminhar  = st.checkbox("Tenho dificuldade para caminhar / subir escadas")
        plano_saude   = st.checkbox("Tenho plano de saúde", value=True)
        sem_medico    = st.checkbox("Já deixei de ir ao médico por custo")

    diabetes_val = st.selectbox("Diabetes", options=list(DIABETES_LABELS.keys()),
                                 format_func=lambda x: DIABETES_LABELS[x])

    genhlth_val = st.selectbox("Como você avalia sua saúde geral?",
                                options=list(GENHLTH_LABELS.keys()),
                                format_func=lambda x: GENHLTH_LABELS[x], index=2)

    col8, col9 = st.columns(2)
    with col8:
        ment_hlth = st.slider("Dias com saúde mental ruim (último mês)", 0, 30, 0)
    with col9:
        phys_hlth = st.slider("Dias com problemas físicos (último mês)", 0, 30, 0)

    # SEÇÃO 3 — Hábitos de vida
    st.markdown('<div class="section-label">Hábitos de vida</div>', unsafe_allow_html=True)
    col10, col11 = st.columns(2)
    with col10:
        fumante      = st.checkbox("Já fumei mais de 100 cigarros na vida")
        alcoolismo   = st.checkbox("Consumo pesado de álcool")
    with col11:
        atividade    = st.checkbox("Pratiquei atividade física nos últimos 30 dias", value=True)
        frutas       = st.checkbox("Como frutas todos os dias", value=True)
        vegetais     = st.checkbox("Como vegetais todos os dias", value=True)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Calcular meu risco cardíaco →")


# ── Processamento e resultado ─────────────────────────────────────────────────
if submitted:
    bmi, bmi_cat = calcular_bmi(peso, altura)
    healthy_lifestyle = sum([
        int(atividade), int(frutas), int(vegetais),
        int(not alcoolismo), int(not fumante),
    ])

    payload = {
        "BMI": bmi, "BMI_cat": bmi_cat,
        "HighBP": int(pressao_alta), "HighChol": int(colesterol),
        "CholCheck": int(check_col), "Smoker": int(fumante),
        "Stroke": int(avc), "Diabetes": diabetes_val,
        "PhysActivity": int(atividade), "Fruits": int(frutas),
        "Veggies": int(vegetais), "HvyAlcoholConsump": int(alcoolismo),
        "AnyHealthcare": int(plano_saude), "NoDocbcCost": int(sem_medico),
        "GenHlth": genhlth_val, "MentHlth": float(ment_hlth),
        "PhysHlth": float(phys_hlth), "DiffWalk": int(dif_caminhar),
        "Sex": sexo, "Age": age_val,
        "Education": edu_val, "Income": income_val,
        "HealthyLifestyle": healthy_lifestyle,
    }

    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        pct      = float(data["probabilidade_pct"].replace("%", ""))
        nivel    = data["risco"]["label"]
        cor      = data["risco"]["color"]
        css_cls  = css_class_nivel(nivel)
        bar_pct  = min(pct, 100)
        bmi_cats = ["Abaixo do peso", "Normal", "Sobrepeso", "Obeso"]

        st.markdown("---")

        # Card principal de resultado
        st.markdown(f"""
        <div class="result-card {css_cls}">
            <div class="result-pct" style="color:{cor}">{pct}%</div>
            <div class="result-label" style="color:{cor}">Risco {nivel}</div>
            <div class="risk-bar-wrap">
                <div class="risk-bar-fill" style="width:{bar_pct}%; background:{cor};"></div>
            </div>
            <div class="result-aviso">
                ⚕️ Este resultado é uma <strong>estimativa de triagem</strong> baseada em
                dados populacionais. Não substitui avaliação médica profissional.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Detalhes do perfil calculado
        st.markdown('<div class="section-label">Seu perfil calculado</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("IMC", f"{bmi}", bmi_cats[bmi_cat])
        c2.metric("Score de hábitos", f"{healthy_lifestyle}/5")
        c3.metric("Modelo", "XGBoost", "AUC 0.85")

        # Orientação baseada no nível
        st.markdown('<div class="section-label">O que isso significa?</div>', unsafe_allow_html=True)
        orientacoes = {
            "Baixo": (
                "✅ Seu perfil indica baixo risco cardíaco com base nos dados informados. "
                "Continue mantendo hábitos saudáveis e faça check-ups regulares."
            ),
            "Moderado": (
                "⚠️ Seu perfil indica risco moderado. Considere conversar com um médico "
                "sobre seus fatores de risco e adotar hábitos mais saudáveis."
            ),
            "Alto": (
                "🔶 Seu perfil indica risco elevado. Recomendamos fortemente agendar "
                "uma consulta médica para avaliação detalhada."
            ),
            "Muito Alto": (
                "🔴 Seu perfil indica risco muito alto. Procure um médico o quanto antes "
                "para uma avaliação cardiovascular completa."
            ),
        }
        st.info(orientacoes.get(nivel, ""))

    except requests.exceptions.ConnectionError:
        st.error("❌ Não foi possível conectar à API. Verifique se ela está rodando em http://127.0.0.1:8000")
    except Exception as e:
        st.error(f"❌ Erro ao processar: {e}")
        