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


import random
from typing import Union, List, Tuple


class GeneradorIncognitaTriple(GeneradorProblema):
    """
    Genera ecuaciones lineales sencillas con tres términos en el lado izquierdo
    y un resultado constante en el lado derecho: a + b + c = d.
    
    Uno de los términos (a, b o c) se reemplaza aleatoriamente por la incógnita 'x',
    pudiendo llevar signo positivo (+x) o negativo (-x).
    
    Ejemplos de salida:
        - x - 3 - 12 = -9
        -8 + x + 10 = 6
        15 - 4 - x = 2
    """
    NOMBRE_TIPO = "Ecuación Lineal (3 Términos)"

    def generar(self, dificultad: Union[int, NivelDificultad, None] = None) -> ProblemaMatematico:
        nivel = self._validar_dificultad(dificultad)

        # 1. Definir rangos según el nivel de dificultad
        if nivel == NivelDificultad.FACIL:
            limite_val, limite_x = 10, 10
        elif nivel == NivelDificultad.INTERMEDIO:
            limite_val, limite_x = 25, 20
        else:  # NivelDIFICIL / Avanzado
            limite_val, limite_x = 50, 40

        # 2. Generar el valor real de 'x' (evitamos el 0 para mantener el interés)
        x_valor = random.choice([i for i in range(-limite_x, limite_x + 1) if i != 0])
        
        # 3. Elegir la posición de 'x' (0 = posición a, 1 = posición b, 2 = posición c)
        posicion_x = random.randint(0, 2)
        
        # 4. Elegir el signo de 'x' (+1 o -1)
        signo_x = random.choice([1, -1])

        # 5. Generar valores numéricos constantes para las otras dos posiciones
        rango_constantes = [i for i in range(-limite_val, limite_val + 1) if i != 0]
        num_constante1 = random.choice(rango_constantes)
        num_constante2 = random.choice(rango_constantes)

        # 6. Construir la estructura de términos y calcular el término 'd' (resultado)
        terminos_evaluados: List[int] = []
        partes_pregunta: List[str] = []

        idx_constante = 0
        constantes = [num_constante1, num_constante2]

        for i in range(3):
            if i == posicion_x:
                # Evaluación matemática del término con x
                val_termino = signo_x * x_valor
                terminos_evaluados.append(val_termino)
                
                # Representación textual de 'x'
                str_x = self._formatear_termino_x(i, signo_x)
                partes_pregunta.append(str_x)
            else:
                # Evaluación matemática del número constante
                val_num = constantes[idx_constante]
                idx_constante += 1
                terminos_evaluados.append(val_num)
                
                # Representación textual del número
                str_num = self._formatear_termino_numero(i, val_num)
                partes_pregunta.append(str_num)

        # 7. Calcular el lado derecho de la ecuación (d = a + b + c)
        d = sum(terminos_evaluados)

        # 8. Unir todos los componentes en una cadena legible
        pregunta = f"{' '.join(partes_pregunta)} = {d}"

        return ProblemaMatematico(
            pregunta=pregunta,
            solucion=x_valor,
            dificultad=nivel,
            tipo_problema=self.NOMBRE_TIPO
        )

    # -------------------------------------------------------------------------
    # Métodos Auxiliares de Formato
    # -------------------------------------------------------------------------

    def _formatear_termino_x(self, posicion: int, signo: int) -> str:
        """Da formato a 'x' o '-x' dependiendo de si es el primer término o subsiguiente."""
        if posicion == 0:
            return "x" if signo == 1 else "- x"
        else:
            return "+ x" if signo == 1 else "- x"

    def _formatear_termino_numero(self, posicion: int, numero: int) -> str:
        """Da formato a los números con sus respectivos signos y espacios."""
        if posicion == 0:
            return f"{numero}"
        else:
            if numero >= 0:
                return f"+ {numero}"
            else:
                return f"- {abs(numero)}"

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