const API_URL = 'http://127.0.0.1:8000';

const BMI_CATS = ['Abaixo do peso', 'Peso normal', 'Sobrepeso', 'Obesidade'];

const INTERPRETACOES = {
    'Baixo':
        'O perfil informado indica risco cardiovascular baixo em relação à população de referência. ' +
        'Recomenda-se manter os hábitos saudáveis atuais e realizar consultas preventivas periódicas.',
    'Moderado':
        'O perfil informado indica risco cardiovascular moderado. Recomenda-se atenção aos fatores ' +
        'de risco identificados e consulta a profissional de saúde para orientação individualizada.',
    'Alto':
        'O perfil informado indica risco cardiovascular elevado. Recomenda-se fortemente agendar ' +
        'consulta médica para avaliação detalhada dos fatores de risco e definição de medidas preventivas.',
    'Muito Alto':
        'O perfil informado indica risco cardiovascular muito elevado. Recomenda-se buscar avaliação ' +
        'médica com brevidade para uma análise cardiovascular abrangente e definição de condutas adequadas.',
};

function calcularBMI(peso, altura) {
    const h = altura / 100;
    const bmi = peso / (h * h);
    const bmiArred = Math.round(bmi * 10) / 10;
    let cat;
    if (bmi < 18.5)      cat = 0;
    else if (bmi < 25.0) cat = 1;
    else if (bmi < 30.0) cat = 2;
    else                 cat = 3;
    return { bmi: bmiArred, bmiCat: cat };
}

function atualizarBMI() {
    const peso    = parseFloat(document.getElementById('peso').value);
    const altura  = parseFloat(document.getElementById('altura').value);
    const preview = document.getElementById('bmi-preview');

    if (!peso || !altura || peso <= 0 || altura <= 0) {
        preview.classList.add('hidden');
        return;
    }

    const { bmi, bmiCat } = calcularBMI(peso, altura);
    document.getElementById('bmi-value').textContent    = bmi.toFixed(1);
    document.getElementById('bmi-cat-label').textContent = '— ' + BMI_CATS[bmiCat];
    preview.classList.remove('hidden');
}

['menthlth', 'physhlth'].forEach(id => {
    const input  = document.getElementById(id);
    const output = document.getElementById(id + '-val');
    input.addEventListener('input', () => { output.value = input.value; });
});

document.getElementById('peso').addEventListener('input', atualizarBMI);
document.getElementById('altura').addEventListener('input', atualizarBMI);

document.getElementById('form-risco').addEventListener('submit', async (e) => {
    e.preventDefault();

    const btn = document.getElementById('btn-submit');
    btn.disabled    = true;
    btn.textContent = 'Calculando...';

    try {
        const peso   = parseFloat(document.getElementById('peso').value);
        const altura = parseFloat(document.getElementById('altura').value);
        const { bmi, bmiCat } = calcularBMI(peso, altura);

        const physActivity = document.getElementById('physactivity').checked;
        const fruits       = document.getElementById('fruits').checked;
        const veggies      = document.getElementById('veggies').checked;
        const hvyAlcohol   = document.getElementById('hvyalcohol').checked;
        const smoker       = document.getElementById('smoker').checked;

        const healthyLifestyle = [physActivity, fruits, veggies, !hvyAlcohol, !smoker]
            .filter(Boolean).length;

        const payload = {
            BMI:               bmi,
            BMI_cat:           bmiCat,
            HighBP:            document.getElementById('highbp').checked     ? 1 : 0,
            HighChol:          document.getElementById('highchol').checked   ? 1 : 0,
            CholCheck:         document.getElementById('cholcheck').checked  ? 1 : 0,
            Smoker:            smoker      ? 1 : 0,
            Stroke:            document.getElementById('stroke').checked     ? 1 : 0,
            Diabetes:          parseInt(document.getElementById('diabetes').value),
            PhysActivity:      physActivity ? 1 : 0,
            Fruits:            fruits       ? 1 : 0,
            Veggies:           veggies      ? 1 : 0,
            HvyAlcoholConsump: hvyAlcohol   ? 1 : 0,
            AnyHealthcare:     document.getElementById('anyhealthcare').checked ? 1 : 0,
            NoDocbcCost:       document.getElementById('nodoccost').checked     ? 1 : 0,
            GenHlth:           parseInt(document.getElementById('genhlth').value),
            MentHlth:          parseFloat(document.getElementById('menthlth').value),
            PhysHlth:          parseFloat(document.getElementById('physhlth').value),
            DiffWalk:          document.getElementById('diffwalk').checked   ? 1 : 0,
            Sex:               parseInt(document.getElementById('sexo').value),
            Age:               parseInt(document.getElementById('age').value),
            Education:         parseInt(document.getElementById('education').value),
            Income:            parseInt(document.getElementById('income').value),
            HealthyLifestyle:  healthyLifestyle,
        };

        const response = await fetch(`${API_URL}/predict`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload),
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `Erro HTTP ${response.status}`);
        }

        const data = await response.json();
        renderizarResultado(data, bmi, bmiCat, healthyLifestyle);

    } catch (err) {
        renderizarErro(err.message);
    } finally {
        btn.disabled    = false;
        btn.textContent = 'Calcular estimativa de risco';
    }
});

function cssClass(label) {
    return { 'Baixo': 'baixo', 'Moderado': 'moderado', 'Alto': 'alto', 'Muito Alto': 'muito-alto' }[label] || 'baixo';
}

function renderizarResultado(data, bmi, bmiCat, healthyLifestyle) {
    const pct    = parseFloat(data.probabilidade_pct);
    const nivel  = data.risco.label;
    const cor    = data.risco.color;
    const css    = cssClass(nivel);
    const barPct = Math.min(pct, 100);

    document.getElementById('result-content').innerHTML = `
        <div class="result-card ${css}">
            <div class="result-header">
                <div class="result-prob" style="color:${cor}">${pct}%</div>
                <div class="result-info">
                    <div class="result-tag">Probabilidade estimada</div>
                    <div class="result-classification" style="color:${cor}">Risco ${nivel}</div>
                </div>
            </div>
            <div class="risk-bar">
                <div class="risk-bar-fill" style="width:${barPct}%; background:${cor};"></div>
            </div>
        </div>

        <div class="result-meta">
            <div class="meta-item">
                <div class="meta-value">${bmi.toFixed(1)}</div>
                <div class="meta-label">IMC<br>${BMI_CATS[bmiCat]}</div>
            </div>
            <div class="meta-item">
                <div class="meta-value">${healthyLifestyle}/5</div>
                <div class="meta-label">Score de hábitos<br>saudáveis</div>
            </div>
            <div class="meta-item">
                <div class="meta-value">${data.threshold_usado}</div>
                <div class="meta-label">Limiar de<br>classificação</div>
            </div>
        </div>

        <div class="result-interpretation ${css}">
            ${INTERPRETACOES[nivel] || ''}
        </div>
    `;

    const secao = document.getElementById('resultado');
    secao.classList.remove('hidden');
    secao.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderizarErro(msg) {
    document.getElementById('result-content').innerHTML =
        `<div class="error-msg">Erro ao processar a solicitação: ${msg}</div>`;
    document.getElementById('resultado').classList.remove('hidden');
}

atualizarBMI();
