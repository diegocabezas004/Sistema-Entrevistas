"""Pruebas del ai_client: parseo, validación de campos y reintento (RF-11/RF-12).

No llaman a la API real: se sustituye `_call_api` por respuestas controladas,
así las pruebas corren sin API key y sin costo (importante para la defensa).
"""

from __future__ import annotations

import pytest

from app.ai_client import AIClient, AIResponseError
from app.config import Settings


def _settings(retries: int = 1) -> Settings:
    """Settings de prueba con una API key ficticia (no se usa red)."""
    return Settings(
        anthropic_api_key="test-key",
        anthropic_model="claude-haiku-4-5",
        anthropic_max_tokens=500,
        ai_max_retries=retries,
        database_url="sqlite:///:memory:",
        app_host="127.0.0.1",
        app_port=8000,
    )


def test_json_valido_se_parsea_y_devuelve(monkeypatch):
    client = AIClient(settings=_settings())
    monkeypatch.setattr(
        client, "_call_api", lambda s, u: '{"pregunta": "¿Qué es una API?", "tema": "web"}'
    )

    result = client.generate_json(
        user_prompt="genera pregunta",
        required_fields=["pregunta", "tema"],
    )

    assert result.data["pregunta"] == "¿Qué es una API?"
    assert result.intentos == 1
    assert result.model == "claude-haiku-4-5"
    assert result.raw_response  # se guarda para trazabilidad


def test_extrae_json_dentro_de_fences_markdown(monkeypatch):
    client = AIClient(settings=_settings())
    monkeypatch.setattr(
        client, "_call_api", lambda s, u: '```json\n{"puntaje": 8}\n```'
    )

    result = client.generate_json("evalúa", required_fields=["puntaje"])
    assert result.data["puntaje"] == 8


def test_reintenta_una_vez_y_luego_tiene_exito(monkeypatch):
    client = AIClient(settings=_settings(retries=1))
    respuestas = iter(["no soy json", '{"ok": true}'])
    monkeypatch.setattr(client, "_call_api", lambda s, u: next(respuestas))

    result = client.generate_json("x", required_fields=["ok"])
    assert result.data["ok"] is True
    assert result.intentos == 2  # falló la 1ra, pasó en la 2da


def test_error_controlado_si_falta_campo_tras_reintentos(monkeypatch):
    client = AIClient(settings=_settings(retries=1))
    monkeypatch.setattr(client, "_call_api", lambda s, u: '{"otro": 1}')

    with pytest.raises(AIResponseError) as exc:
        client.generate_json("x", required_fields=["pregunta"])
    assert "pregunta" in str(exc.value)
    assert exc.value.raw_response  # conserva la respuesta cruda


def test_error_controlado_si_json_invalido_persistente(monkeypatch):
    client = AIClient(settings=_settings(retries=1))
    monkeypatch.setattr(client, "_call_api", lambda s, u: "sigo sin ser json")

    with pytest.raises(AIResponseError):
        client.generate_json("x", required_fields=["ok"])
