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

    def __init__(self):
        super().__init__()
        self._ejercicios_usados = set()

    def generar(
        self,
        dificultad: Union[int, NivelDificultad, None] = None
    ) -> ProblemaMatematico:

        nivel = self._validar_dificultad(dificultad)

        while True:

            if nivel == NivelDificultad.FACIL:
                x = random.randint(2, 10)
                y = random.randint(1, 10)

            elif nivel == NivelDificultad.INTERMEDIO:
                x = random.randint(5, 20)
                y = random.randint(5, 20)

            else:
                rango = [
                    i for i in range(-15, 16)
                    if i != 0
                ]

                x = random.choice(rango)
                y = random.choice(rango)

            suma = x + y
            producto = x * y

            # La pregunta queda determinada por suma y producto.
            clave = (nivel, suma, producto)

            if clave not in self._ejercicios_usados:
                self._ejercicios_usados.add(clave)
                break

        pregunta = (
            f"Encuentra dos números 'x' e 'y' tales que:\n"
            f"  x + y = {suma}\n"
            f"  x × y = {producto}"
        )

        return ProblemaMatematico(
            pregunta=pregunta,
            solucion=(x, y),
            dificultad=nivel,
            tipo_problema=self.NOMBRE_TIPO
        )

import random
from typing import Union, List, Tuple


class GeneradorIncognitaTriple(GeneradorProblema):
    """
    Genera ecuaciones lineales simples equivalentes a la versión Rust:

        ax + b = c

    Los rangos de x, a y b dependen del nivel de dificultad.
    Tanto x como a y b pueden tener signo positivo o negativo.

    Ejemplos de salida:
        - 4x + 7 = 31
        - -3x - 5 = 28
        - 8x + 12 = -52
    """

    NOMBRE_TIPO = "Ecuación Lineal Simple"

    def generar(
        self,
        dificultad: Union[int, NivelDificultad, None] = None
    ) -> ProblemaMatematico:

        nivel = self._validar_dificultad(dificultad)

        # ---------------------------------------------------------------------
        # 1. Rangos equivalentes a obtener_rangos() de Rust
        # ---------------------------------------------------------------------

        if nivel == NivelDificultad.FACIL:
            rango_x = (3, 15)
            rango_a = (2, 5)
            rango_b = (1, 10)

        elif nivel == NivelDificultad.INTERMEDIO:
            rango_x = (10, 20)
            rango_a = (4, 8)
            rango_b = (5, 15)

        else:  # NivelDIFICIL / Avanzado
            rango_x = (20, 30)
            rango_a = (6, 12)
            rango_b = (10, 25)

        # ---------------------------------------------------------------------
        # 2. Generar x
        # ---------------------------------------------------------------------

        x_valor = random.randint(*rango_x)

        # Equivalente a:
        #
        # if rng.gen_bool(0.5) {
        #     x = -x;
        # }

        if random.random() < 0.5:
            x_valor = -x_valor

        # ---------------------------------------------------------------------
        # 3. Generar a con signo aleatorio
        # ---------------------------------------------------------------------

        a = random.randint(*rango_a)

        if random.random() < 0.5:
            a = -a

        # ---------------------------------------------------------------------
        # 4. Generar b con signo aleatorio
        # ---------------------------------------------------------------------

        b = random.randint(*rango_b)

        if random.random() < 0.5:
            b = -b

        # ---------------------------------------------------------------------
        # 5. Calcular c
        #
        #       ax + b = c
        #
        # Esto garantiza que x sea siempre una solución exacta.
        # ---------------------------------------------------------------------

        c = (a * x_valor) + b

        # ---------------------------------------------------------------------
        # 6. Formatear b exactamente como en Rust
        # ---------------------------------------------------------------------

        if b < 0:
            signo_b = f"- {abs(b)}"
        else:
            signo_b = f"+ {b}"

        pregunta = f"{a}x {signo_b} = {c}"

        # ---------------------------------------------------------------------
        # 7. Crear el problema
        # ---------------------------------------------------------------------

        return ProblemaMatematico(
            pregunta=pregunta,
            solucion=x_valor,
            dificultad=nivel,
            tipo_problema=self.NOMBRE_TIPO
        )

class GeneradorCombinadoMultiplicacion(GeneradorProblema):
    """
    Genera ecuaciones con paréntesis equivalentes a la versión Rust:

        a(x + b) - d = c

    Los rangos de x, a, b y d dependen del nivel de dificultad.

    Ejemplos de salida:
        - 3(x + 5) - 7 = 38
        - -6(x - 8) + 12 = -18
        - 10(x + 15) - 20 = 80
    """

    NOMBRE_TIPO = "Ecuación con Paréntesis"

    def generar(
        self,
        dificultad: Union[int, NivelDificultad, None] = None
    ) -> ProblemaMatematico:

        nivel = self._validar_dificultad(dificultad)

        # ---------------------------------------------------------------------
        # 1. Rangos equivalentes a obtener_rangos() de Rust
        # ---------------------------------------------------------------------

        if nivel == NivelDificultad.FACIL:
            rango_x = (3, 15)
            rango_a = (2, 5)
            rango_b = (1, 10)
            rango_d = (1, 10)

        elif nivel == NivelDificultad.INTERMEDIO:
            rango_x = (10, 20)
            rango_a = (4, 8)
            rango_b = (5, 15)
            rango_d = (5, 15)

        else:  # NivelDIFICIL / Avanzado
            rango_x = (20, 30)
            rango_a = (6, 12)
            rango_b = (10, 25)
            rango_d = (10, 25)

        # ---------------------------------------------------------------------
        # 2. Generar x con signo aleatorio
        # ---------------------------------------------------------------------

        x_valor = random.randint(*rango_x)

        if random.random() < 0.5:
            x_valor = -x_valor

        # ---------------------------------------------------------------------
        # 3. Generar a con signo aleatorio
        # ---------------------------------------------------------------------

        a = random.randint(*rango_a)

        if random.random() < 0.5:
            a = -a

        # ---------------------------------------------------------------------
        # 4. Generar b con signo aleatorio
        # ---------------------------------------------------------------------

        b = random.randint(*rango_b)

        if random.random() < 0.5:
            b = -b

        # ---------------------------------------------------------------------
        # 5. Generar d con signo aleatorio
        # ---------------------------------------------------------------------

        d = random.randint(*rango_d)

        if random.random() < 0.5:
            d = -d

        # ---------------------------------------------------------------------
        # 6. Calcular c
        #
        #       a(x + b) - d = c
        #
        # Esto garantiza que x sea siempre una solución exacta.
        # ---------------------------------------------------------------------

        c = a * (x_valor + b) - d

        # ---------------------------------------------------------------------
        # 7. Formatear b
        # ---------------------------------------------------------------------

        if b < 0:
            signo_b = f"- {abs(b)}"
        else:
            signo_b = f"+ {b}"

        # ---------------------------------------------------------------------
        # 8. Formatear d
        #
        # Rust hace:
        #
        # d < 0  -> "+ abs(d)"
        # d >= 0 -> "- d"
        #
        # porque la expresión es:
        #
        #       a(x + b) - d
        # ---------------------------------------------------------------------

        if d < 0:
            signo_d = f"+ {abs(d)}"
        else:
            signo_d = f"- {d}"

        pregunta = f"{a}(x {signo_b}) {signo_d} = {c}"

        # ---------------------------------------------------------------------
        # 9. Crear el problema
        # ---------------------------------------------------------------------

        return ProblemaMatematico(
            pregunta=pregunta,
            solucion=x_valor,
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