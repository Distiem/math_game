"""
models.py
Modelos de datos para la aplicación de Matemáticas Interactivas.
"""

from dataclasses import dataclass, asdict
from enum import IntEnum
from typing import Any


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

    def to_dict(self):
        return {
            "pregunta": self.pregunta,
            "solucion": self.solucion,
            "dificultad": self.dificultad.value,
            "dificultad_nombre": self.dificultad.name,
            "tipo_problema": self.tipo_problema,
        }