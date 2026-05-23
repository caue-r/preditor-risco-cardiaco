from pydantic import BaseModel, Field, field_validator
from typing import Literal


class PredictRequest(BaseModel):
    # ── Dados calculados automaticamente ─────────────────────────────────────
    BMI: float = Field(..., ge=12, le=55, description="IMC calculado de peso/altura")
    BMI_cat: int = Field(..., ge=0, le=3, description="0=Abaixo peso, 1=Normal, 2=Sobrepeso, 3=Obeso")

    # ── Perguntas sim/não (0 ou 1) ────────────────────────────────────────────
    HighBP: int = Field(..., ge=0, le=1, description="Pressão alta diagnosticada?")
    HighChol: int = Field(..., ge=0, le=1, description="Colesterol alto diagnosticado?")
    CholCheck: int = Field(..., ge=0, le=1, description="Check de colesterol nos últimos 5 anos?")
    Smoker: int = Field(..., ge=0, le=1, description="Fumou mais de 100 cigarros na vida?")
    Stroke: int = Field(..., ge=0, le=1, description="Já teve AVC?")
    PhysActivity: int = Field(..., ge=0, le=1, description="Atividade física nos últimos 30 dias?")
    Fruits: int = Field(..., ge=0, le=1, description="Consome frutas diariamente?")
    Veggies: int = Field(..., ge=0, le=1, description="Consome vegetais diariamente?")
    HvyAlcoholConsump: int = Field(..., ge=0, le=1, description="Consumo pesado de álcool?")
    AnyHealthcare: int = Field(..., ge=0, le=1, description="Tem plano de saúde?")
    NoDocbcCost: int = Field(..., ge=0, le=1, description="Deixou de ir ao médico por custo?")
    DiffWalk: int = Field(..., ge=0, le=1, description="Dificuldade para caminhar ou subir escadas?")
    Sex: int = Field(..., ge=0, le=1, description="Sexo: 0=Feminino, 1=Masculino")

    # ── Escalas ───────────────────────────────────────────────────────────────
    Diabetes: int = Field(..., ge=0, le=2, description="0=Não, 1=Pré-diabetes, 2=Confirmado")
    GenHlth: int = Field(..., ge=1, le=5, description="Saúde geral: 1=Excelente, 5=Ruim")
    MentHlth: float = Field(..., ge=0, le=30, description="Dias com saúde mental ruim (0-30)")
    PhysHlth: float = Field(..., ge=0, le=30, description="Dias com problemas físicos (0-30)")
    Age: int = Field(..., ge=1, le=13, description="Faixa etária: 1=18-24 até 13=80+")
    Education: int = Field(..., ge=1, le=6, description="Escolaridade: 1=Nunca estudou, 6=Superior")
    Income: int = Field(..., ge=1, le=8, description="Renda: 1=Baixa, 8=Alta")

    # ── Feature calculada ─────────────────────────────────────────────────────
    HealthyLifestyle: int = Field(..., ge=0, le=5, description="Score de hábitos saudáveis (calculado)")

    model_config = {"json_schema_extra": {"example": {
        "BMI": 28.4, "BMI_cat": 2,
        "HighBP": 1, "HighChol": 0, "CholCheck": 1,
        "Smoker": 0, "Stroke": 0, "Diabetes": 0,
        "PhysActivity": 1, "Fruits": 1, "Veggies": 1,
        "HvyAlcoholConsump": 0, "AnyHealthcare": 1, "NoDocbcCost": 0,
        "GenHlth": 3, "MentHlth": 2, "PhysHlth": 1,
        "DiffWalk": 0, "Sex": 1, "Age": 7,
        "Education": 5, "Income": 5, "HealthyLifestyle": 4,
    }}}


class RiskLevel(BaseModel):
    label: str
    color: str     # para o frontend usar diretamente


class PredictResponse(BaseModel):
    probabilidade: float = Field(..., description="Probabilidade de risco cardíaco (0.0 a 1.0)")
    probabilidade_pct: str = Field(..., description="Ex: '67.3%'")
    risco: RiskLevel
    alerta: bool = Field(..., description="True se probabilidade >= threshold")
    threshold_usado: float
    modelo: str
    aviso: str = "Este resultado é uma estimativa de triagem e não substitui avaliação médica profissional."


class HealthCheckResponse(BaseModel):
    status: str
    modelo: str
    auc_roc: float
    recall: float
    threshold: float
    features: int
