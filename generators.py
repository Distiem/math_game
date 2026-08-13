"""
generators.py
Generadores de problemas matemáticos.
"""

import random
from abc import ABC, abstractmethod
from typing import Union

from models import NivelDificultad, ProblemaMatematico


class GeneradorProblema(ABC):
    """Clase base abstracta para todos los generadores de problemas."""

    def __init__(self, dificultad_defecto: Union[int, NivelDificultad] = NivelDificultad.FACIL):
        self.dificultad_defecto = NivelDificultad(dificultad_defecto)

    def _validar_dificultad(self, dificultad: Union[int, NivelDificultad, None]) -> NivelDificultad:
        if dificultad is None:
            return self.dificultad_defecto
        return NivelDificultad(dificultad)

    @abstractmethod
    def generar(self, dificultad: Union[int, NivelDificultad, None] = None) -> ProblemaMatematico:
        pass


class GeneradorSumaProducto(GeneradorProblema):
    """Genera ejercicios donde se debe hallar dos números a partir de su suma y su producto."""
    NOMBRE_TIPO = "Suma y Producto"

    def generar(self, dificultad: Union[int, NivelDificultad, None] = None) -> ProblemaMatematico:
        nivel = self._validar_dificultad(dificultad)
        if nivel == NivelDificultad.FACIL:
            x = random.randint(1, 10)
            y = random.randint(1, 10)
        elif nivel == NivelDificultad.INTERMEDIO:
            x = random.randint(5, 20)
            y = random.randint(5, 20)
        else:
            rango_negativos = [i for i in range(-15, 16) if i != 0]
            x = random.choice(rango_negativos)
            y = random.choice(rango_negativos)
        suma = x + y
        producto = x * y
        pregunta = f"Encuentra dos números 'x' e 'y' tales que:\n  x + y = {suma}\n  x × y = {producto}"
        return ProblemaMatematico(
            pregunta=pregunta,
            solucion=(x, y),
            dificultad=nivel,
            tipo_problema=self.NOMBRE_TIPO
        )


class GeneradorIncognitaTriple(GeneradorProblema):
    """Genera ejercicios de operaciones de tres términos con una incógnita."""
    NOMBRE_TIPO = "Incógnita Triple"

    def generar(self, dificultad: Union[int, NivelDificultad, None] = None) -> ProblemaMatematico:
        nivel = self._validar_dificultad(dificultad)
        op1 = random.choice(["+", "-"])
        op2 = random.choice(["+", "-"])
        if nivel == NivelDificultad.FACIL:
            a = random.randint(1, 15)
            b = random.randint(1, 15)
            incognita = random.randint(1, 15)
        elif nivel == NivelDificultad.INTERMEDIO:
            a = random.randint(10, 40)
            b = random.randint(10, 40)
            incognita = random.randint(5, 30)
        else:
            a = random.randint(20, 100)
            b = random.randint(20, 100)
            incognita = random.randint(10, 50)
        paso1 = a + b if op1 == "+" else a - b
        c = paso1 + incognita if op2 == "+" else paso1 - incognita
        pregunta = f"{a} {op1} {b} {op2} ? = {c}"
        return ProblemaMatematico(
            pregunta=pregunta,
            solucion=incognita,
            dificultad=nivel,
            tipo_problema=self.NOMBRE_TIPO
        )


class GeneradorCombinadoMultiplicacion(GeneradorProblema):
    """Genera ejercicios combinados de multiplicación y suma/resta."""
    NOMBRE_TIPO = "Combinado Multiplicación"

    def generar(self, dificultad: Union[int, NivelDificultad, None] = None) -> ProblemaMatematico:
        nivel = self._validar_dificultad(dificultad)
        a = random.choice([i for i in range(-9, 10) if i != 0])
        if nivel == NivelDificultad.FACIL:
            limite_b, limite_c = 10, 20
        elif nivel == NivelDificultad.INTERMEDIO:
            limite_b, limite_c = 15, 50
        else:
            limite_b, limite_c = 25, 100
        rango_b = [i for i in range(-limite_b, limite_b + 1) if i != 0]
        rango_c = [i for i in range(-limite_c, limite_c + 1) if i != 0]
        b = random.choice(rango_b)
        c = random.choice(rango_c)
        operador = random.choice(["+", "-"])
        if operador == "+":
            respuesta = (a * b) + c
        else:
            respuesta = (a * b) - c
        str_a = f"{a}"
        str_b = f"({b})" if b < 0 else f"{b}"
        str_c = f"({c})" if c < 0 else f"{c}"
        pregunta = f"{str_a} × {str_b} {operador} {str_c} = ?"
        return ProblemaMatematico(
            pregunta=pregunta,
            solucion=respuesta,
            dificultad=nivel,
            tipo_problema=self.NOMBRE_TIPO
        )


# ── Registro de generadores ──────────────────────────────────────────────────
GENERADORES = {
    "suma_producto": GeneradorSumaProducto(),
    "incognita_triple": GeneradorIncognitaTriple(),
    "combinado_multiplicacion": GeneradorCombinadoMultiplicacion(),
}

TIPOS_PROBLEMA = list(GENERADORES.keys())