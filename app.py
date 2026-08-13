"""
app.py
"""

import random

from flask import Flask, render_template, request, jsonify, session

from generators import GENERADORES, TIPOS_PROBLEMA
from database import (
    init_db,
    get_or_create_session,
    get_raw_stats,
    record_answer,
    calcular_estadisticas,
    reset_session,
)

app = Flask(__name__)
app.secret_key = "matematicas-secreto-2026-modular"

# Inicializar base de datos al arrancar
init_db()

# ── Estado en memoria para problemas activos ─────────────────────────────────
problemas_activos = {}
contador_problemas = 0


# ═══════════════════════════════════════════════════════════════════════════════
# RUTAS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    # Asegurar que existe una sesión en la cookie y en SQLite
    sid = session.get("session_id")
    sid = get_or_create_session(sid)
    session["session_id"] = sid
    return render_template("index.html")


@app.route("/api/problem")
def api_problem():
    global contador_problemas

    diff = request.args.get("difficulty", "1", type=int)
    tipo_solicitado = request.args.get("type", "aleatorio")

    if tipo_solicitado == "aleatorio" or tipo_solicitado not in GENERADORES:
        tipo = random.choice(TIPOS_PROBLEMA)
    else:
        tipo = tipo_solicitado

    generador = GENERADORES[tipo]
    problema = generador.generar(dificultad=diff)

    contador_problemas += 1
    pid = f"p{contador_problemas}"
    problemas_activos[pid] = problema

    data = problema.to_dict()
    data["id"] = pid
    return jsonify(data)


@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.get_json()
    pid = data.get("problem_id")
    respuesta_raw = data.get("answer", "").strip()
    tiempo = data.get("tiempo", 0)

    problema = problemas_activos.get(pid)
    if not problema:
        return jsonify({"error": "Problema no encontrado"}), 404

    # ── Validar respuesta ────────────────────────────────────────────────────
    sol = problema.solucion
    correcto = False

    if isinstance(sol, tuple):
        # Suma y Producto: acepta "x, y" o "x y"
        try:
            partes = respuesta_raw.replace(",", " ").split()
            nums = [int(p) for p in partes if p.lstrip("-").isdigit()]
            if len(nums) >= 2:
                correcto = (nums[0] == sol[0] and nums[1] == sol[1]) or \
                           (nums[0] == sol[1] and nums[1] == sol[0])
        except Exception:
            correcto = False
    else:
        try:
            correcto = int(respuesta_raw) == sol
        except Exception:
            correcto = False

    # ── Persistir en SQLite ──────────────────────────────────────────────────
    sid = session.get("session_id")
    if not sid:
        sid = get_or_create_session(None)
        session["session_id"] = sid

    stats = record_answer(
        session_id=sid,
        correcto=correcto,
        tiempo=tiempo,
        tipo_problema=problema.tipo_problema,
        dificultad=problema.dificultad.name,
        respuesta_usuario=respuesta_raw,
        respuesta_correcta=str(sol),
    )

    # ── Mensaje de feedback ──────────────────────────────────────────────────
    if correcto:
        mensaje = f"La respuesta era {sol}."
        if tiempo < 3:
            mensaje += " ¡Rápido!"
        elif tiempo > 10:
            mensaje += " Pero tardaste bastante..."
    else:
        mensaje = f"La respuesta correcta era {sol}."

    return jsonify({
        "correct": correcto,
        "message": mensaje,
        "stats": calcular_estadisticas(stats),
    })


@app.route("/api/stats")
def api_stats():
    sid = session.get("session_id")
    if not sid:
        return jsonify(calcular_estadisticas(get_raw_stats("")))
    stats = get_raw_stats(sid)
    return jsonify(calcular_estadisticas(stats))


@app.route("/api/reset", methods=["POST"])
def api_reset():
    sid = session.get("session_id")
    if sid:
        new_id = reset_session(sid)
        session["session_id"] = new_id
    return jsonify({"ok": True})


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("=" * 60)
    app.run(debug=False, host="0.0.0.0", port=5000)