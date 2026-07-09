"""Módulo de validación (RF-11, RF-12, RNF-04).

Valida configuración, respuestas, rangos y la estructura/coherencia de las
salidas de la IA antes de persistir o mostrar nada.
"""

from app.validation.constants import (
    IDIOMAS,
    MAX_PREGUNTAS,
    MIN_PREGUNTAS,
    NIVELES,
    PUNTAJE_MAX,
    PUNTAJE_MIN,
    TIPOS_ENTREVISTA,
)
from app.validation.errors import ValidationError
from app.validation.validators import (
    InterviewConfig,
    normalizar_idioma,
    normalizar_nivel,
    normalizar_tipo,
    validar_cantidad_preguntas,
    validar_config,
    validar_puntaje,
    validar_respuesta,
    validar_salida_evaluacion,
    validar_salida_pregunta,
    validar_salida_resumen,
    validar_texto_obligatorio,
)

__all__ = [
    "ValidationError",
    "InterviewConfig",
    "NIVELES",
    "TIPOS_ENTREVISTA",
    "IDIOMAS",
    "PUNTAJE_MIN",
    "PUNTAJE_MAX",
    "MIN_PREGUNTAS",
    "MAX_PREGUNTAS",
    "normalizar_nivel",
    "normalizar_tipo",
    "normalizar_idioma",
    "validar_config",
    "validar_respuesta",
    "validar_puntaje",
    "validar_cantidad_preguntas",
    "validar_texto_obligatorio",
    "validar_salida_pregunta",
    "validar_salida_evaluacion",
    "validar_salida_resumen",
]
