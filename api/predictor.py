import joblib
import json
import pandas as pd
from pathlib import Path

# ── Caminhos (relativos à raiz do projeto) ────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "heart_disease_model.pkl"
META_PATH  = BASE_DIR / "model" / "heart_disease_metadata.json"


class Predictor:
    def __init__(self):
        self.model    = joblib.load(MODEL_PATH)
        self.metadata = json.loads(META_PATH.read_text(encoding="utf-8"))
        self.features  = self.metadata["features"]
        self.threshold = self.metadata["threshold_default"]
        self.model_name = self.metadata["model_name"]

    def _nivel_risco(self, pct: float) -> dict:
        if pct < 15:
            return {"label": "Baixo",      "color": "#1D9E75"}
        elif pct < 35:
            return {"label": "Moderado",   "color": "#EF9F27"}
        elif pct < 60:
            return {"label": "Alto",       "color": "#E07020"}
        else:
            return {"label": "Muito Alto", "color": "#D85A30"}

    def predict(self, dados: dict) -> dict:
        X = pd.DataFrame([dados])[self.features]
        proba = float(self.model.predict_proba(X)[0, 1])
        pct   = round(proba * 100, 1)

        return {
            "probabilidade":     round(proba, 4),
            "probabilidade_pct": f"{pct}%",
            "risco":             self._nivel_risco(pct),
            "alerta":            proba >= self.threshold,
            "threshold_usado":   self.threshold,
            "modelo":            self.model_name,
        }


# Instância única — carregada uma vez ao subir o servidor
predictor = Predictor()


def calcular_bmi(peso_kg: float, altura_cm: float) -> tuple[float, int]:
    """Calcula IMC e categoria a partir de peso e altura."""
    h   = altura_cm / 100
    bmi = round(peso_kg / h ** 2, 1)
    if bmi < 18.5:  cat = 0
    elif bmi < 25:  cat = 1
    elif bmi < 30:  cat = 2
    else:           cat = 3
    return bmi, cat


def calcular_healthy_lifestyle(
    atividade_fisica: bool,
    come_frutas: bool,
    come_vegetais: bool,
    sem_alcoolismo: bool,
    nao_fumante: bool,
) -> int:
    """Score de hábitos saudáveis de 0 a 5."""
    return sum([
        int(atividade_fisica),
        int(come_frutas),
        int(come_vegetais),
        int(sem_alcoolismo),
        int(nao_fumante),
    ])
