"""
database.py
Capa de persistencia SQLite para estadísticas e historial.
"""

import sqlite3
import json
import uuid
from pathlib import Path

DB_PATH = Path(__file__).parent / "matematicas.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea las tablas si no existen."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id   TEXT PRIMARY KEY,
                total        INTEGER DEFAULT 0,
                correctas    INTEGER DEFAULT 0,
                incorrectas  INTEGER DEFAULT 0,
                racha_actual INTEGER DEFAULT 0,
                mejor_racha  INTEGER DEFAULT 0,
                tiempos_json TEXT DEFAULT '[]',
                created_at   TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS answers (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id        TEXT NOT NULL,
                tipo_problema     TEXT,
                dificultad        TEXT,
                correcto          INTEGER,
                respuesta_usuario TEXT,
                respuesta_correcta TEXT,
                tiempo            REAL,
                created_at        TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
        """)
        conn.commit()


def create_session() -> str:
    """Crea una nueva sesión y devuelve su ID."""
    sid = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sessions (session_id) VALUES (?)",
            (sid,)
        )
        conn.commit()
    return sid


def get_or_create_session(session_id: str | None) -> str:
    """Devuelve un session_id válido, creando uno nuevo si es necesario."""
    if session_id:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT session_id FROM sessions WHERE session_id = ?",
                (session_id,)
            ).fetchone()
            if row:
                return row["session_id"]
    return create_session()


def get_raw_stats(session_id: str) -> dict:
    """Devuelve las estadísticas crudas de una sesión."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if not row:
            return {
                "total": 0, "correctas": 0, "incorrectas": 0,
                "racha_actual": 0, "mejor_racha": 0,
                "tiempos": [], "historial": []
            }
        return {
            "total": row["total"],
            "correctas": row["correctas"],
            "incorrectas": row["incorrectas"],
            "racha_actual": row["racha_actual"],
            "mejor_racha": row["mejor_racha"],
            "tiempos": json.loads(row["tiempos_json"]),
            "historial": get_history(session_id),
        }


def get_history(session_id: str) -> list:
    """Devuelve el historial de respuestas de una sesión."""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT tipo_problema, dificultad, correcto,
                      respuesta_usuario, respuesta_correcta, tiempo
               FROM answers
               WHERE session_id = ?
               ORDER BY id ASC""",
            (session_id,)
        ).fetchall()
        return [
            {
                "tipo": r["tipo_problema"],
                "dificultad": r["dificultad"],
                "correcto": bool(r["correcto"]),
                "respuesta_usuario": r["respuesta_usuario"],
                "respuesta_correcta": r["respuesta_correcta"],
                "tiempo": r["tiempo"],
            }
            for r in rows
        ]


def record_answer(
    session_id: str,
    correcto: bool,
    tiempo: float,
    tipo_problema: str,
    dificultad: str,
    respuesta_usuario: str,
    respuesta_correcta: str,
) -> dict:
    """Registra una respuesta y actualiza las estadísticas agregadas.
       Devuelve el dict de estadísticas actualizado."""

    with get_conn() as conn:
        # 1. Insertar respuesta en historial
        conn.execute(
            """INSERT INTO answers
               (session_id, tipo_problema, dificultad, correcto,
                respuesta_usuario, respuesta_correcta, tiempo)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, tipo_problema, dificultad, int(correcto),
             respuesta_usuario, respuesta_correcta, round(tiempo, 2))
        )

        # 2. Leer stats actuales
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()

        total = row["total"] + 1
        correctas = row["correctas"] + (1 if correcto else 0)
        incorrectas = row["incorrectas"] + (0 if correcto else 1)
        racha_actual = row["racha_actual"] + 1 if correcto else 0
        mejor_racha = max(row["mejor_racha"], racha_actual)
        tiempos = json.loads(row["tiempos_json"])
        if correcto:
            tiempos.append(round(tiempo, 2))

        # 3. Guardar stats actualizadas
        conn.execute(
            """UPDATE sessions
               SET total = ?, correctas = ?, incorrectas = ?,
                   racha_actual = ?, mejor_racha = ?, tiempos_json = ?
               WHERE session_id = ?""",
            (total, correctas, incorrectas, racha_actual, mejor_racha,
             json.dumps(tiempos), session_id)
        )
        conn.commit()

    return get_raw_stats(session_id)


def calcular_estadisticas(stats: dict) -> dict:
    """Calcula métricas derivadas a partir de las estadísticas crudas."""
    total = stats["total"]
    correctas = stats["correctas"]
    incorrectas = stats["incorrectas"]
    tiempos = stats["tiempos"]

    precision = round((correctas / total) * 100, 1) if total > 0 else 0.0
    tiempo_promedio = round(sum(tiempos) / len(tiempos), 1) if tiempos else 0.0
    mejor_tiempo = round(min(tiempos), 1) if tiempos else 0.0
    peor_tiempo = round(max(tiempos), 1) if tiempos else 0.0

    return {
        "total": total,
        "correctas": correctas,
        "incorrectas": incorrectas,
        "precision": precision,
        "tiempo_promedio": tiempo_promedio,
        "mejor_tiempo": mejor_tiempo,
        "peor_tiempo": peor_tiempo,
        "racha_actual": stats["racha_actual"],
        "mejor_racha": stats["mejor_racha"],
        "tiempos": tiempos,
        "historial": stats.get("historial", []),
    }


def reset_session(session_id: str) -> str:
    """Borra las respuestas y reinicia las stats de una sesión.
        Devuelve un nuevo session_id."""
    new_id = create_session()
    with get_conn() as conn:
        conn.execute("DELETE FROM answers WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
    return new_id