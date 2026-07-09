"""Pruebas del motor de generación de preguntas (RF-02, RF-11).

Se usa un cliente de IA simulado (stub) que devuelve un AICallResult controlado,
para no llamar a la API real. Así se verifica la orquestación, la validación de
coherencia y que las preguntas previas lleguen al prompt (anti-repetición RF-02).
"""

from __future__ import annotations

import pytest

from app.ai_client import AICallResult
from app.questions_engine import QuestionsEngine, construir_prompt_pregunta
from app.validation import InterviewConfig, ValidationError


def _config(nivel: str = "junior", idioma: str = "es") -> InterviewConfig:
    return InterviewConfig(
        rol="Backend Developer",
        tecnologia="Python",
        nivel=nivel,
        idioma=idioma,
        cantidad_preguntas=3,
        tipo="conceptual",
    )


class _StubClient:
    """Cliente de IA falso: devuelve un JSON fijo y registra lo que recibió."""

    def __init__(self, data: dict):
        self._data = data
        self.ultimo_user_prompt = ""
        self.ultimo_system_prompt = ""

    def generate_json(self, user_prompt, required_fields, system_prompt="", criterios=None):
        self.ultimo_user_prompt = user_prompt
        self.ultimo_system_prompt = system_prompt
        return AICallResult(
            data=self._data,
            raw_response="{...}",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="claude-haiku-4-5",
        )


def test_genera_pregunta_valida():
    stub = _StubClient(
        {
            "pregunta": "¿Qué es una variable en Python?",
            "dificultad": "junior",
            "criterios_evaluados": ["claridad"],
            "tema": "Fundamentos",
        }
    )
    engine = QuestionsEngine(client=stub)
    q = engine.generar_pregunta(_config())

    assert q.pregunta.startswith("¿Qué es una variable")
    assert q.dificultad == "junior"
    assert q.tema == "Fundamentos"
    assert q.trace.model == "claude-haiku-4-5"  # trazabilidad presente
    assert q.resumen()["criterios_evaluados"] == ["claridad"]


def test_pregunta_incoherente_con_nivel_falla_rf11():
    # La IA responde con dificultad 'senior' en una entrevista 'junior'.
    stub = _StubClient(
        {
            "pregunta": "Diseña un sistema de colas distribuido",
            "dificultad": "senior",
            "criterios_evaluados": [],
            "tema": "Arquitectura",
        }
    )
    engine = QuestionsEngine(client=stub)
    with pytest.raises(ValidationError):
        engine.generar_pregunta(_config(nivel="junior"))


def test_preguntas_previas_llegan_al_prompt_rf02():
    stub = _StubClient(
        {
            "pregunta": "Nueva pregunta",
            "dificultad": "junior",
            "criterios_evaluados": [],
            "tema": "X",
        }
    )
    engine = QuestionsEngine(client=stub)
    engine.generar_pregunta(_config(), preguntas_previas=["¿Qué es una lista?"])

    # El prompt debe incluir la pregunta previa para evitar repetición.
    assert "¿Qué es una lista?" in stub.ultimo_user_prompt


def test_prompt_incluye_idioma_ingles():
    prompt = construir_prompt_pregunta(_config(idioma="en"))
    assert "English" in prompt


def test_prompt_sin_previas_indica_que_no_hay():
    prompt = construir_prompt_pregunta(_config())
    assert "ninguna pregunta" in prompt.lower()
