"""
app.py
"""

import random
import io
from datetime import datetime

from flask import Flask, render_template, request, jsonify, session, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

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
import os
app.secret_key = os.environ.get("SECRET_KEY", "clave-secreta-por-defecto-muy-segura")

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
        mensaje = f"¡Bien hecho!"
        if tiempo < 3:
            mensaje += " ¡Rápido!"
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
# EXPORTAR PDF
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/export_pdf")
def export_pdf():
    sid = session.get("session_id")
    if not sid:
        return jsonify({"error": "No hay sesión activa"}), 400

    raw = get_raw_stats(sid)
    stats = calcular_estadisticas(raw)
    historial = raw.get("historial", [])

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )
    elements.append(Paragraph("🧠 Matemáticas Interactivas", title_style))

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    elements.append(Paragraph(f"Reporte de estadísticas — {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1')))
    elements.append(Spacer(1, 16))

    # Estadísticas principales
    stats_data = [
        ["Métrica", "Valor"],
        ["Preguntas totales", str(stats["total"])],
        ["Correctas", str(stats["correctas"])],
        ["Incorrectas", str(stats["incorrectas"])],
        ["Precisión", f"{stats['precision']} %"],
        ["Tiempo promedio", f"{stats['tiempo_promedio']} s"],
        ["Mejor tiempo", f"{stats['mejor_tiempo']} s"],
        ["Peor tiempo", f"{stats['peor_tiempo']} s"],
        ["Racha actual", str(stats["racha_actual"])],
        ["Mejor racha", str(stats["mejor_racha"])],
    ]

    stats_table = Table(stats_data, colWidths=[8*cm, 8*cm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.HexColor('#ffffff')]),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 24))

    # Historial
    if historial:
        elements.append(Paragraph("📝 Historial de respuestas", styles['Heading2']))
        elements.append(Spacer(1, 8))

        hist_data = [["#", "Tipo", "Dificultad", "Resultado", "Tu respuesta", "Correcta", "Tiempo"]]
        for i, h in enumerate(historial, 1):
            hist_data.append([
                str(i),
                h["tipo"],
                h["dificultad"],
                "✅ Correcto" if h["correcto"] else "❌ Incorrecto",
                h["respuesta_usuario"],
                h["respuesta_correcta"],
                f"{h['tiempo']:.1f} s",
            ])

        hist_table = Table(hist_data, colWidths=[1.2*cm, 3.5*cm, 2.5*cm, 2.8*cm, 2.5*cm, 2.2*cm, 1.8*cm])
        hist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.HexColor('#ffffff')]),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('TEXTCOLOR', (3, 1), (3, -1), colors.HexColor('#16a34a')),
        ]))
        # Color rojo para incorrectos
        for i, h in enumerate(historial, 1):
            if not h["correcto"]:
                hist_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#dc2626')),
                ]))

        elements.append(hist_table)

    # Footer
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER,
    )
    elements.append(Paragraph("Generado por Matemáticas Interactivas — matematicas-interactivas.app", footer_style))

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"estadisticas_matematicas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
