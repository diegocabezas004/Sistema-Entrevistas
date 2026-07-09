"""Validaciones del sistema (RF-11, RF-12, RNF-04).

Cubre tres frentes:
  1. Entrada del usuario  -> configuración de entrevista y respuestas.
  2. Rangos y formatos     -> puntajes, cantidades.
  3. Salidas de la IA      -> estructura y coherencia de los JSON generados.

Todas las funciones lanzan `ValidationError` con un mensaje claro y el campo
afectado, para que la UI/API muestre exactamente qué corregir (RNF-06).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.validation.constants import (
    _ALIAS_IDIOMA,
    _ALIAS_NIVEL,
    _ALIAS_TIPO,
    IDIOMAS,
    MAX_LONGITUD_RESPUESTA,
    MAX_PREGUNTAS,
    MIN_LONGITUD_RESPUESTA,
    MIN_PREGUNTAS,
    NIVELES,
    PUNTAJE_MAX,
    PUNTAJE_MIN,
    TIPOS_ENTREVISTA,
)
from app.validation.errors import ValidationError


@dataclass(frozen=True)
class InterviewConfig:
    """Configuración de entrevista ya validada y normalizada (RF-01).

    Que sea inmutable y normalizada garantiza que el resto del sistema
    (questions_engine, evaluation_engine) reciba siempre datos consistentes.
    """

    rol: str
    tecnologia: str
    nivel: str            # normalizado: junior|intermedio|senior
    idioma: str           # normalizado: es|en
    cantidad_preguntas: int
    tipo: str             # normalizado: tecnica|conceptual|...|mixta


# ---------------------------------------------------------------------------
# Normalizadores de catálogo (toleran acentos, mayúsculas y sinónimos)
# ---------------------------------------------------------------------------
def normalizar_nivel(valor: str) -> str:
    clave = (valor or "").strip().lower()
    normalizado = _ALIAS_NIVEL.get(clave, clave)
    if normalizado not in NIVELES:
        raise ValidationError(
            f"Nivel no válido: '{valor}'. Debe ser uno de: {', '.join(NIVELES)}.",
            campo="nivel",
        )
    return normalizado


def normalizar_tipo(valor: str) -> str:
    clave = (valor or "").strip().lower()
    normalizado = _ALIAS_TIPO.get(clave, clave)
    if normalizado not in TIPOS_ENTREVISTA:
        raise ValidationError(
            f"Tipo de entrevista no válido: '{valor}'. "
            f"Opciones: {', '.join(TIPOS_ENTREVISTA)}.",
            campo="tipo",
        )
    return normalizado


def normalizar_idioma(valor: str) -> str:
    clave = (valor or "").strip().lower()
    normalizado = _ALIAS_IDIOMA.get(clave, clave)
    if normalizado not in IDIOMAS:
        raise ValidationError(
            f"Idioma no válido: '{valor}'. Opciones: {', '.join(IDIOMAS)}.",
            campo="idioma",
        )
    return normalizado


# ---------------------------------------------------------------------------
# 1. Configuración de entrevista (RF-01 / RNF-04)
# ---------------------------------------------------------------------------
def validar_texto_obligatorio(valor: Any, campo: str, maximo: int = 200) -> str:
    """Valida que un campo de texto no esté vacío y no exceda el máximo."""
    if not isinstance(valor, str):
        raise ValidationError(f"'{campo}' debe ser texto.", campo=campo)
    limpio = valor.strip()
    if not limpio:
        raise ValidationError(f"'{campo}' no puede estar vacío.", campo=campo)
    if len(limpio) > maximo:
        raise ValidationError(
            f"'{campo}' es demasiado largo (máx. {maximo} caracteres).", campo=campo
        )
    return limpio


def validar_cantidad_preguntas(valor: Any) -> int:
    """Valida la cantidad de preguntas dentro del rango permitido."""
    try:
        n = int(valor)
    except (TypeError, ValueError):
        raise ValidationError(
            "La cantidad de preguntas debe ser un número entero.",
            campo="cantidad_preguntas",
        )
    if not (MIN_PREGUNTAS <= n <= MAX_PREGUNTAS):
        raise ValidationError(
            f"La cantidad de preguntas debe estar entre {MIN_PREGUNTAS} "
            f"y {MAX_PREGUNTAS}.",
            campo="cantidad_preguntas",
        )
    return n


def validar_config(datos: dict[str, Any]) -> InterviewConfig:
    """Valida y normaliza la configuración completa de una entrevista (RF-01).

    Rechaza configuración vacía o incompleta antes de iniciar (RNF-04).
    """
    if not isinstance(datos, dict) or not datos:
        raise ValidationError("La configuración de la entrevista está vacía.")

    return InterviewConfig(
        rol=validar_texto_obligatorio(datos.get("rol"), "rol"),
        tecnologia=validar_texto_obligatorio(datos.get("tecnologia"), "tecnologia"),
        nivel=normalizar_nivel(datos.get("nivel", "")),
        idioma=normalizar_idioma(datos.get("idioma", "")),
        cantidad_preguntas=validar_cantidad_preguntas(datos.get("cantidad_preguntas")),
        tipo=normalizar_tipo(datos.get("tipo", "")),
    )


# ---------------------------------------------------------------------------
# 2. Respuesta del usuario (RNF-04)
# ---------------------------------------------------------------------------
def validar_respuesta(texto: Any) -> str:
    """Valida la respuesta del usuario a una pregunta (no vacía, longitud)."""
    if not isinstance(texto, str):
        raise ValidationError("La respuesta debe ser texto.", campo="respuesta")
    limpio = texto.strip()
    if len(limpio) < MIN_LONGITUD_RESPUESTA:
        raise ValidationError(
            "La respuesta no puede estar vacía.", campo="respuesta"
        )
    if len(limpio) > MAX_LONGITUD_RESPUESTA:
        raise ValidationError(
            f"La respuesta es demasiado larga (máx. {MAX_LONGITUD_RESPUESTA} "
            "caracteres).",
            campo="respuesta",
        )
    return limpio


# ---------------------------------------------------------------------------
# 3. Rangos y formatos
# ---------------------------------------------------------------------------
def validar_puntaje(valor: Any, campo: str = "puntaje") -> int:
    """Valida que un puntaje sea numérico y esté en el rango 0–100."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidationError(f"'{campo}' debe ser numérico.", campo=campo)
    if not (PUNTAJE_MIN <= valor <= PUNTAJE_MAX):
        raise ValidationError(
            f"'{campo}' fuera de rango ({PUNTAJE_MIN}–{PUNTAJE_MAX}): {valor}.",
            campo=campo,
        )
    return int(round(valor))


def _validar_lista_de_texto(valor: Any, campo: str) -> list[str]:
    """Valida que un campo sea una lista de cadenas (permite lista vacía)."""
    if not isinstance(valor, list):
        raise ValidationError(f"'{campo}' debe ser una lista.", campo=campo)
    for item in valor:
        if not isinstance(item, str):
            raise ValidationError(
                f"'{campo}' debe contener solo textos.", campo=campo
            )
    return [i.strip() for i in valor]


# ---------------------------------------------------------------------------
# 4. Estructura y coherencia de las salidas de la IA (RF-11 / RF-12 / RNF-04)
# ---------------------------------------------------------------------------
def validar_salida_pregunta(
    data: dict[str, Any], config: InterviewConfig | None = None
) -> dict[str, Any]:
    """Valida la estructura del JSON de una pregunta generada (§6a).

    Además comprueba coherencia con la configuración (RF-11): la dificultad de la
    pregunta debe coincidir con el nivel configurado.
    """
    pregunta = validar_texto_obligatorio(
        data.get("pregunta"), "pregunta", maximo=MAX_LONGITUD_RESPUESTA
    )
    dificultad = normalizar_nivel(data.get("dificultad", ""))
    criterios = _validar_lista_de_texto(
        data.get("criterios_evaluados", []), "criterios_evaluados"
    )
    tema = validar_texto_obligatorio(data.get("tema"), "tema")

    if config is not None and dificultad != config.nivel:
        raise ValidationError(
            f"Incoherencia (RF-11): la pregunta es de nivel '{dificultad}' pero "
            f"la entrevista está configurada como '{config.nivel}'.",
            campo="dificultad",
        )

    return {
        "pregunta": pregunta,
        "dificultad": dificultad,
        "criterios_evaluados": criterios,
        "tema": tema,
    }


def validar_salida_evaluacion(data: dict[str, Any]) -> dict[str, Any]:
    """Valida la estructura del JSON de evaluación de una respuesta (§6b)."""
    puntaje = validar_puntaje(data.get("puntaje"))
    coherente = data.get("coherente_con_configuracion")
    if not isinstance(coherente, bool):
        raise ValidationError(
            "'coherente_con_configuracion' debe ser booleano.",
            campo="coherente_con_configuracion",
        )
    return {
        "puntaje": puntaje,
        "fortalezas": _validar_lista_de_texto(data.get("fortalezas", []), "fortalezas"),
        "errores": _validar_lista_de_texto(data.get("errores", []), "errores"),
        "omisiones": _validar_lista_de_texto(data.get("omisiones", []), "omisiones"),
        "respuesta_mejorada": validar_texto_obligatorio(
            data.get("respuesta_mejorada"),
            "respuesta_mejorada",
            maximo=MAX_LONGITUD_RESPUESTA,
        ),
        "coherente_con_configuracion": coherente,
    }


def validar_salida_resumen(data: dict[str, Any]) -> dict[str, Any]:
    """Valida la estructura del JSON del resumen/plan de mejora (§6c)."""
    return {
        "nivel_estimado": normalizar_nivel(data.get("nivel_estimado", "")),
        "puntaje_general": validar_puntaje(
            data.get("puntaje_general"), campo="puntaje_general"
        ),
        "areas_fuertes": _validar_lista_de_texto(
            data.get("areas_fuertes", []), "areas_fuertes"
        ),
        "areas_mejora": _validar_lista_de_texto(
            data.get("areas_mejora", []), "areas_mejora"
        ),
        "plan_de_estudio": _validar_lista_de_texto(
            data.get("plan_de_estudio", []), "plan_de_estudio"
        ),
    }
