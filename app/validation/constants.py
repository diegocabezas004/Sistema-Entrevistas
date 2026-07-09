"""Valores permitidos del dominio (una sola fuente de verdad).

Centralizar aquí los catálogos evita "strings mágicos" repartidos por el código
y facilita validar coherencia (RF-11). Si mañana se agrega un nivel o un tipo de
entrevista, se cambia solo aquí.
"""

from __future__ import annotations

# Niveles de dificultad (coinciden con el campo "dificultad" de la IA, §6).
NIVELES: tuple[str, ...] = ("junior", "intermedio", "senior")

# Tipos de entrevista soportados (RF-01).
TIPOS_ENTREVISTA: tuple[str, ...] = (
    "tecnica",
    "conceptual",
    "practica",
    "situacional",
    "arquitectura",
    "mixta",
)

# Idiomas soportados para las preguntas/evaluaciones (RF-01).
IDIOMAS: tuple[str, ...] = ("es", "en")

# Rango del puntaje. Se usa una escala 0–100 en todo el sistema (por pregunta y
# general) para no mezclar escalas. Documentado para la defensa.
PUNTAJE_MIN: int = 0
PUNTAJE_MAX: int = 100

# Límites de la cantidad de preguntas por entrevista (RF-01 / RNF-04).
MIN_PREGUNTAS: int = 1
MAX_PREGUNTAS: int = 20

# Longitud mínima/máxima razonable de una respuesta del usuario (RNF-04).
MIN_LONGITUD_RESPUESTA: int = 1
MAX_LONGITUD_RESPUESTA: int = 5000

# Alias comunes que la gente escribe → forma canónica. Tolerante a acentos y
# sinónimos, para no rechazar entradas válidas por una tilde.
_ALIAS_NIVEL = {
    "jr": "junior",
    "básico": "junior",
    "basico": "junior",
    "principiante": "junior",
    "intermedio": "intermedio",
    "medio": "intermedio",
    "mid": "intermedio",
    "sr": "senior",
    "avanzado": "senior",
    "experto": "senior",
}

_ALIAS_TIPO = {
    "técnica": "tecnica",
    "tecnica": "tecnica",
    "conceptual": "conceptual",
    "práctica": "practica",
    "practica": "practica",
    "situacional": "situacional",
    "arquitectura básica": "arquitectura",
    "arquitectura basica": "arquitectura",
    "arquitectura": "arquitectura",
    "diseño": "arquitectura",
    "diseno": "arquitectura",
    "mixta": "mixta",
    "mixto": "mixta",
}

_ALIAS_IDIOMA = {
    "es": "es",
    "español": "es",
    "espanol": "es",
    "castellano": "es",
    "spanish": "es",
    "en": "en",
    "inglés": "en",
    "ingles": "en",
    "english": "en",
}
