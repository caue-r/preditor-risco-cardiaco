from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import PredictRequest, PredictResponse, HealthCheckResponse
from predictor import predictor, calcular_bmi, calcular_healthy_lifestyle

app = FastAPI(
    title="Heart Disease Risk API",
    description="Predição de risco cardíaco com base em perguntas simples. "
                "Modelo XGBoost treinado no dataset BRFSS 2015 (CDC).",
    version="1.0.0",
)

# ── CORS — permite o Streamlit (e qualquer frontend local) chamar a API ──────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # em produção: restringir ao domínio do frontend
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Rotas ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Geral"])
def root():
    return {
        "mensagem": "Heart Disease Risk API está no ar.",
        "docs":     "/docs",
        "health":   "/health",
        "predict":  "/predict",
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Geral"])
def health():
    """Verifica se o modelo está carregado e retorna métricas principais."""
    meta = predictor.metadata
    return {
        "status":    "ok",
        "modelo":    meta["model_name"],
        "auc_roc":   meta["auc_roc"],
        "recall":    meta["recall"],
        "threshold": meta["threshold_default"],
        "features":  len(meta["features"]),
    }


@app.post("/predict", response_model=PredictResponse, tags=["Predição"])
def predict(dados: PredictRequest):
    """
    Recebe os dados do formulário e retorna a probabilidade de risco cardíaco.

    Campos calculados automaticamente pelo frontend (não perguntar ao usuário):
    - **BMI** e **BMI_cat**: derivados de peso e altura
    - **HealthyLifestyle**: derivado de PhysActivity, Fruits, Veggies,
      HvyAlcoholConsump e Smoker
    """
    try:
        resultado = predictor.predict(dados.model_dump())
        return PredictResponse(**resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calcular-bmi", tags=["Utilitários"])
def endpoint_calcular_bmi(peso_kg: float, altura_cm: float):
    """
    Calcula IMC e categoria a partir de peso e altura.
    O frontend chama isso antes de montar o payload do /predict.
    """
    if peso_kg <= 0 or altura_cm <= 0:
        raise HTTPException(status_code=422, detail="Peso e altura devem ser positivos.")
    bmi, cat = calcular_bmi(peso_kg, altura_cm)
    labels = {0: "Abaixo do peso", 1: "Normal", 2: "Sobrepeso", 3: "Obeso"}
    return {
        "bmi":       bmi,
        "bmi_cat":   cat,
        "categoria": labels[cat],
    }
