/* app.js — Frontend de Matemáticas Interactivas */

let currentProblem = null;
let difficulty = 1;
let startTime = 0;
let timerInterval = null;
let answered = false;
let stats = {
    total: 0, correctas: 0, incorrectas: 0,
    tiempos: [], racha_actual: 0, mejor_racha: 0,
    historial: []
};

function setDifficulty(d) {
    difficulty = d;
    document.querySelectorAll('.diff-btn').forEach(btn => {
        btn.classList.toggle('active', parseInt(btn.dataset.diff) === d);
    });
}

function startGame() {
    document.getElementById('startOverlay').classList.add('hidden');
    document.getElementById('gameContent').classList.remove('hidden');
    nextProblem();
}

function startTimer() {
    startTime = Date.now();
    const badge = document.getElementById('timerBadge');
    badge.classList.remove('urgent');
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        badge.textContent = `⏱ ${elapsed} s`;
        if (elapsed > 10) badge.classList.add('urgent');
    }, 100);
}

function stopTimer() {
    clearInterval(timerInterval);
    return ((Date.now() - startTime) / 1000);
}

let problemType = 'aleatorio';

function setProblemType(type) {
    problemType = type;
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === type);
    });
}

async function nextProblem() {
    answered = false;
    document.getElementById('answerInput').value = '';
    document.getElementById('answerInput').disabled = false;
    document.getElementById('answerInput').focus();
    document.getElementById('submitBtn').classList.remove('hidden');
    document.getElementById('nextBtn').classList.add('hidden');
    document.getElementById('feedback').classList.remove('show');
    document.getElementById('problemText').textContent = 'Cargando...';

    const url = `/api/problem?difficulty=${difficulty}&type=${encodeURIComponent(problemType)}`;
    const res = await fetch(url);
    currentProblem = await res.json();

    document.getElementById('tipoBadge').textContent = currentProblem.tipo_problema;
    document.getElementById('diffBadge').textContent = currentProblem.dificultad_nombre;
    document.getElementById('problemText').textContent = currentProblem.pregunta;
    startTimer();
}

async function checkAnswer() {
    if (answered) return;
    const input = document.getElementById('answerInput');
    const raw = input.value.trim();
    if (!raw) return;

    answered = true;
    input.disabled = true;
    const tiempo = stopTimer();
    document.getElementById('submitBtn').classList.add('hidden');
    document.getElementById('nextBtn').classList.remove('hidden');
    document.getElementById('nextBtn').focus();

    const res = await fetch('/api/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            problem_id: currentProblem.id,
            answer: raw,
            tiempo: tiempo
        })
    });
    const data = await res.json();

    // Actualizar estadísticas locales
    stats.total = data.stats.total;
    stats.correctas = data.stats.correctas;
    stats.incorrectas = data.stats.incorrectas;
    stats.precision = data.stats.precision;
    stats.tiempo_promedio = data.stats.tiempo_promedio;
    stats.mejor_tiempo = data.stats.mejor_tiempo;
    stats.peor_tiempo = data.stats.peor_tiempo;
    stats.tiempos = data.stats.tiempos;
    stats.racha_actual = data.stats.racha_actual;
    stats.mejor_racha = data.stats.mejor_racha;
    stats.historial = data.stats.historial;

    renderStats();
    renderHistory();

    const fb = document.getElementById('feedback');
    fb.className = 'feedback show ' + (data.correct ? 'correct' : 'incorrect');
    if (data.correct) {
        fb.innerHTML = `✅ ¡Correcto! ${data.message}`;
        if (stats.racha_actual >= 3) showConfetti();
    } else {
        fb.innerHTML = `❌ Incorrecto. ${data.message}`;
    }
}

function renderStats() {
    document.getElementById('statTotal').textContent = stats.total;
    document.getElementById('statCorrect').textContent = stats.correctas;
    document.getElementById('statWrong').textContent = stats.incorrectas;

    document.getElementById('statAccuracy').textContent = stats.precision + ' %';
    document.getElementById('accuracyBar').style.width = stats.precision + '%';

    document.getElementById('statAvgTime').textContent = stats.tiempo_promedio + ' s';
    document.getElementById('statBestTime').textContent = stats.mejor_tiempo + ' s';
    document.getElementById('statWorstTime').textContent = stats.peor_tiempo + ' s';

    document.getElementById('statStreak').textContent = stats.racha_actual;
    document.getElementById('statBestStreak').textContent = stats.mejor_racha;

    const streakDisplay = document.getElementById('streakDisplay');
    if (stats.racha_actual >= 3) {
        streakDisplay.style.display = 'flex';
        document.getElementById('streakCount').textContent = stats.racha_actual;
    } else {
        streakDisplay.style.display = 'none';
    }
}

function renderHistory() {
    const list = document.getElementById('historyList');
    if (stats.historial.length === 0) {
        list.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 20px;">Aún no hay respuestas</div>';
        return;
    }
    list.innerHTML = stats.historial.slice().reverse().map(h => {
        const ok = h.correcto;
        return `
            <div class="history-item ${ok ? 'correct' : 'incorrect'}">
                <div>
                    <div style="font-weight:600;">${h.tipo}</div>
                    <div class="h-type">${h.dificultad}</div>
                </div>
                <div style="text-align:right;">
                    <div class="h-result" style="color: ${ok ? 'var(--success)' : 'var(--danger)'};">${ok ? '✓' : '✗'} ${h.respuesta_usuario}</div>
                    <div class="h-time">⏱ ${h.tiempo.toFixed(1)} s</div>
                </div>
            </div>
        `;
    }).join('');
}

function showConfetti() {
    const colors = ['#38bdf8', '#4ade80', '#fbbf24', '#f87171', '#a78bfa', '#22d3ee'];
    for (let i = 0; i < 30; i++) {
        const el = document.createElement('div');
        el.className = 'confetti';
        el.style.left = Math.random() * 100 + 'vw';
        el.style.background = colors[Math.floor(Math.random() * colors.length)];
        el.style.animationDuration = (1.5 + Math.random()) + 's';
        el.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 3000);
    }
}