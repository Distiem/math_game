import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Union


class NivelDificultad(IntEnum):
    FACIL = 1
    INTERMEDIO = 2
    AVANZADO = 3

@dataclass
class ProblemaMatematico:
    """Contenedor estandarizado para los problemas generados."""
    pregunta: str
    solucion: Any
    dificultad: NivelDificultad
    tipo_problema: str

    def __str__(self) -> str:
        return f"[{self.tipo_problema} - Dificultad {self.dificultad.name}]\n{self.pregunta}\nSolución: {self.solucion}"


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
        """Método abstracto que debe ser implementado por cada generador."""
        pass

# 1. Suma y Producto

class GeneradorSumaProducto(GeneradorProblema):
    """Genera ejercicios donde se debe hallar dos números a partir de su suma y su producto.
    
    """

    NOMBRE_TIPO = "Suma y Producto"

    def generar(self, dificultad: Union[int, NivelDificultad, None] = None) -> ProblemaMatematico:
        nivel = self._validar_dificultad(dificultad)

        if nivel == NivelDificultad.FACIL:
            x = random.randint(1, 10)
            y = random.randint(1, 10)
        elif nivel == NivelDificultad.INTERMEDIO:
            x = random.randint(5, 20)
            y = random.randint(5, 20)
        else:  # AVANZADO
            rango_negativos = [i for i in range(-15, 16) if i != 0]
            x = random.choice(rango_negativos)
            y = random.choice(rango_negativos)

        suma = x + y
        producto = x * y
        pregunta = f"Encuentra dos números 'x' e 'y' tales que:\n  x + y = {suma}\n  x * y = {producto}"

        return ProblemaMatematico(
            pregunta=pregunta,
            solucion=(x, y),
            dificultad=nivel,
            tipo_problema=self.NOMBRE_TIPO
        )

# 2. Incógnita Triple

class GeneradorIncognitaTriple(GeneradorProblema):
    """Genera ejercicios de operaciones de tres términos con una incógnita.

    """

    NOMBRE_TIPO = "Incógnita Triple"

    def generar(self, dificultad: Union[int, NivelDificultad, None] = None) -> ProblemaMatematico:
        nivel = self._validar_dificultad(dificultad)
        op1 = random.choice(['+', '-'])
        op2 = random.choice(['+', '-'])

        if nivel == NivelDificultad.FACIL:
            a = random.randint(1, 15)
            b = random.randint(1, 15)
            incognita = random.randint(1, 15)
        elif nivel == NivelDificultad.INTERMEDIO:
            a = random.randint(10, 40)
            b = random.randint(10, 40)
            incognita = random.randint(5, 30)
        else:  # AVANZADO
            a = random.randint(20, 100)
            b = random.randint(20, 100)
            incognita = random.randint(10, 50)

        paso1 = a + b if op1 == '+' else a - b
        c = paso1 + incognita if op2 == '+' else paso1 - incognita

        pregunta = f"{a} {op1} {b} {op2} ? = {c}"

        return ProblemaMatematico(
            pregunta=pregunta,
            solucion=incognita,
            dificultad=nivel,
            tipo_problema=self.NOMBRE_TIPO
        )

# 3. Combinado Multiplicación

class GeneradorCombinadoMultiplicacion(GeneradorProblema):
    """Genera ejercicios combinados de multiplicación y suma/resta con números positivos y negativos."""

    NOMBRE_TIPO = "Combinado Multiplicación"

    def generar(self, dificultad: Union[int, NivelDificultad, None] = None) -> ProblemaMatematico:
        nivel = self._validar_dificultad(dificultad)
        
        # 'a' se genera entre -9 y 9 (excluyendo el 0) para todos los niveles
        a = random.choice([i for i in range(-9, 10) if i != 0])

        # Definición de rangos para 'b' y 'c' según la dificultad
        if nivel == NivelDificultad.FACIL:
            limite_b = 10
            limite_c = 20
        elif nivel == NivelDificultad.INTERMEDIO:
            limite_b = 15
            limite_c = 50
        else:  # AVANZADO
            limite_b = 25
            limite_c = 100

        # 'b' y 'c' pueden ser positivos o negativos (excluyendo el 0)
        rango_b = [i for i in range(-limite_b, limite_b + 1) if i != 0]
        rango_c = [i for i in range(-limite_c, limite_c + 1) if i != 0]

        b = random.choice(rango_b)
        c = random.choice(rango_c)

        operador = random.choice(['+', '-'])

        # Cálculo de la respuesta correcta
        if operador == '+':
            respuesta = (a * b) + c
        else:
            respuesta = (a * b) - c

        # Formateo visual: coloca paréntesis a los números negativos cuando van después de un operador
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

# 

if __name__ == "__main__":
    generadores = {
        1: GeneradorSumaProducto(),
        2: GeneradorIncognitaTriple(),
        3: GeneradorCombinadoMultiplicacion()
    }

    while True:
        print("\n" + "=" * 45)
        print("       GENERADOR DE PROBLEMAS MATEMÁTICOS")
        print("=" * 45)
        print("1. Suma y Producto")
        print("2. Incógnita Triple")
        print("3. Combinado Multiplicación")
        print("4. Salir")
        print("=" * 45)

        try:
            opcion = int(input("Selecciona una opción: "))

            if opcion == 4:
                print("\n¡Hasta luego!")
                break

            if opcion not in generadores:
                print("\nOpción no válida.")
                continue

            print("\nSelecciona la dificultad:")
            print("1. Fácil")
            print("2. Intermedio")
            print("3. Avanzado")

            dificultad = int(input("Selecciona una dificultad: "))

            if dificultad not in [1, 2, 3]:
                print("\nDificultad no válida.")
                continue

            generador = generadores[opcion]

            # Modo de ejercicios
            while True:
                problema = generador.generar(dificultad)

                print("\n" + "-" * 45)
                print("PROBLEMA")
                print("-" * 45)
                print(problema.pregunta)
                print("-" * 45)

                respuesta_usuario = input("Tu respuesta (o escribe 'salir'): ").strip()

                # Salir de los ejercicios y volver al menú
                if respuesta_usuario.lower() == "salir":
                    print("\nVolviendo al menú...")
                    break

                try:
                    # Caso especial: Suma y Producto
                    if opcion == 1:
                        partes = respuesta_usuario.split()

                        if len(partes) != 2:
                            print("Debes introducir dos números separados por un espacio.")
                            continue

                        respuesta = (int(partes[0]), int(partes[1]))

                        # Aceptamos los números en cualquier orden
                        solucion = problema.solucion

                        if set(respuesta) == set(solucion):
                            print("¡Correcto! 🎉")
                        else:
                            print("Incorrecto ❌.")
                            print(f"La respuesta correcta era: {solucion[0]} y {solucion[1]}")

                    # Incógnita Triple y Multiplicación
                    else:
                        respuesta = int(respuesta_usuario)

                        if respuesta == problema.solucion:
                            print("¡Correcto! 🎉")
                        else:
                            print("Incorrecto ❌")
                            print(f"La respuesta correcta era: {problema.solucion}")

                except ValueError:
                    print("Respuesta no válida. Introduce un número.")

        except ValueError:
            print("\nError: debes introducir un número.")