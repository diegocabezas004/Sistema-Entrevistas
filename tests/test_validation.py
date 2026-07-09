"""Pruebas del módulo de validación (RF-11, RF-12, RNF-04).

Cubre configuración vacía/inválida, respuestas vacías, rangos de puntaje,
estructura de las salidas de IA y coherencia pregunta↔configuración.
"""

from __future__ import annotations

import pytest

from app.validation import (
    InterviewConfig,
    ValidationError,
    normalizar_nivel,
    normalizar_tipo,
    validar_config,
    validar_puntaje,
    validar_respuesta,
    validar_salida_evaluacion,
    validar_salida_pregunta,
    validar_salida_resumen,
)


# --------------------------- Normalización --------------------------- #
@pytest.mark.parametrize(
    "entrada,esperado",
    [("Junior", "junior"), ("SR", "senior"), ("avanzado", "senior"), ("Medio", "intermedio")],
)
def test_normalizar_nivel_acepta_alias(entrada, esperado):
    assert normalizar_nivel(entrada) == esperado


def test_normalizar_tipo_tolera_acentos():
    assert normalizar_tipo("Técnica") == "tecnica"
    assert normalizar_tipo("arquitectura básica") == "arquitectura"


def test_nivel_invalido_lanza_error():
    with pytest.raises(ValidationError) as e:
        normalizar_nivel("dios")
    assert e.value.campo == "nivel"


# --------------------------- Configuración --------------------------- #
def test_config_valida_se_normaliza():
    cfg = validar_config(
        {
            "rol": "  Backend Developer ",
            "tecnologia": "Python",
            "nivel": "JR",
            "idioma": "español",
            "cantidad_preguntas": "5",
            "tipo": "Técnica",
        }
    )
    assert isinstance(cfg, InterviewConfig)
    assert cfg.rol == "Backend Developer"  # se recorta
    assert cfg.nivel == "junior"
    assert cfg.idioma == "es"
    assert cfg.cantidad_preguntas == 5
    assert cfg.tipo == "tecnica"


def test_config_vacia_lanza_error():
    with pytest.raises(ValidationError):
        validar_config({})


def test_config_rol_vacio_lanza_error():
    with pytest.raises(ValidationError) as e:
        validar_config(
            {
                "rol": "   ",
                "tecnologia": "Python",
                "nivel": "junior",
                "idioma": "es",
                "cantidad_preguntas": 3,
                "tipo": "mixta",
            }
        )
    assert e.value.campo == "rol"


def test_cantidad_preguntas_fuera_de_rango():
    with pytest.raises(ValidationError) as e:
        validar_config(
            {
                "rol": "QA",
                "tecnologia": "Selenium",
                "nivel": "junior",
                "idioma": "es",
                "cantidad_preguntas": 999,
                "tipo": "mixta",
            }
        )
    assert e.value.campo == "cantidad_preguntas"


# --------------------------- Respuesta --------------------------- #
def test_respuesta_vacia_lanza_error():
    with pytest.raises(ValidationError):
        validar_respuesta("   ")


def test_respuesta_valida_se_recorta():
    assert validar_respuesta("  una respuesta  ") == "una respuesta"


# --------------------------- Puntaje --------------------------- #
@pytest.mark.parametrize("bueno", [0, 50, 100, 87.5])
def test_puntaje_valido(bueno):
    assert 0 <= validar_puntaje(bueno) <= 100


@pytest.mark.parametrize("malo", [-1, 101, "80", True, None])
def test_puntaje_invalido(malo):
    with pytest.raises(ValidationError):
        validar_puntaje(malo)


# --------------------------- Salidas de IA --------------------------- #
def test_salida_pregunta_valida():
    out = validar_salida_pregunta(
        {
            "pregunta": "¿Qué es la inyección de dependencias?",
            "dificultad": "intermedio",
            "criterios_evaluados": ["claridad", "precisión"],
            "tema": "Diseño de software",
        }
    )
    assert out["dificultad"] == "intermedio"
    assert out["criterios_evaluados"] == ["claridad", "precisión"]


def test_salida_pregunta_incoherente_con_config_rf11():
    cfg = validar_config(
        {
            "rol": "Dev",
            "tecnologia": "Java",
            "nivel": "junior",
            "idioma": "es",
            "cantidad_preguntas": 3,
            "tipo": "conceptual",
        }
    )
    # La IA devuelve una pregunta de nivel senior → incoherente (RF-11).
    with pytest.raises(ValidationError) as e:
        validar_salida_pregunta(
            {
                "pregunta": "Diseña un sistema distribuido",
                "dificultad": "senior",
                "criterios_evaluados": [],
                "tema": "Arquitectura",
            },
            config=cfg,
        )
    assert e.value.campo == "dificultad"


def test_salida_evaluacion_valida():
    out = validar_salida_evaluacion(
        {
            "puntaje": 75,
            "fortalezas": ["buena estructura"],
            "errores": [],
            "omisiones": ["no mencionó complejidad"],
            "respuesta_mejorada": "Una respuesta más completa...",
            "coherente_con_configuracion": True,
        }
    )
    assert out["puntaje"] == 75
    assert out["coherente_con_configuracion"] is True


def test_salida_evaluacion_coherente_no_booleano():
    with pytest.raises(ValidationError) as e:
        validar_salida_evaluacion(
            {
                "puntaje": 50,
                "respuesta_mejorada": "x",
                "coherente_con_configuracion": "sí",  # inválido
            }
        )
    assert e.value.campo == "coherente_con_configuracion"


def test_salida_resumen_valida():
    out = validar_salida_resumen(
        {
            "nivel_estimado": "intermedio",
            "puntaje_general": 68,
            "areas_fuertes": ["algoritmos"],
            "areas_mejora": ["bases de datos"],
            "plan_de_estudio": ["Repasar índices", "Practicar joins"],
        }
    )
    assert out["puntaje_general"] == 68
    assert out["nivel_estimado"] == "intermedio"
