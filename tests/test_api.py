"""Pruebas de la API REST (RF-01…RF-12, RNF-06).

Se sobreescribe la dependencia `get_service` con un servicio simulado (sin IA ni
BD real) para probar los endpoints, los códigos HTTP y el mapeo de errores.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.app import create_app, get_service
from app.ai_client import AIResponseError
from app.validation import ValidationError


class _FakeService:
    """Servicio de entrevista falso: respuestas fijas y errores a demanda."""

    def iniciar_entrevista(self, config_data):
        if config_data.get("nivel") == "malo":
            raise ValidationError("Nivel no válido", campo="nivel")
        return {"entrevista_id": 1, "config": config_data}

    def generar_siguiente_pregunta(self, entrevista_id):
        return {
            "pregunta_id": 10,
            "orden": 1,
            "total": 3,
            "pregunta": "¿Qué es Python?",
            "dificultad": "junior",
            "criterios_evaluados": ["claridad"],
            "tema": "Fundamentos",
        }

    def responder_pregunta(self, entrevista_id, pregunta_id, respuesta):
        return {"pregunta_id": pregunta_id, "puntaje": 80}

    def finalizar_entrevista(self, entrevista_id):
        return {"entrevista_id": entrevista_id, "nivel_estimado": "junior"}

    def obtener_entrevista(self, entrevista_id):
        return None if entrevista_id == 404 else {"id": entrevista_id, "estado": "en_curso"}

    def listar_historial(self):
        return [{"id": 1, "puntaje_general": 70}]

    def obtener_trazas(self, entrevista_id):
        return [{"tipo_llamada": "pregunta", "modelo": "claude-haiku-4-5"}]


@pytest.fixture
def client():
    app = create_app()
    app.dependency_overrides[get_service] = lambda: _FakeService()
    return TestClient(app)


def test_health_incluye_aviso(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert "práctica" in r.json()["aviso"]


def test_iniciar_entrevista(client):
    r = client.post("/entrevistas", json={
        "rol": "Dev", "tecnologia": "Python", "nivel": "junior",
        "idioma": "es", "cantidad_preguntas": 3, "tipo": "conceptual",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["entrevista_id"] == 1
    assert "aviso" in body  # disclaimer presente (§12)


def test_iniciar_con_validacion_de_pydantic(client):
    # cantidad_preguntas fuera de rango → 422 de Pydantic
    r = client.post("/entrevistas", json={
        "rol": "Dev", "tecnologia": "Python", "nivel": "junior",
        "idioma": "es", "cantidad_preguntas": 0, "tipo": "conceptual",
    })
    assert r.status_code == 422


def test_error_de_negocio_devuelve_400(client):
    r = client.post("/entrevistas", json={
        "rol": "Dev", "tecnologia": "Python", "nivel": "malo",
        "idioma": "es", "cantidad_preguntas": 3, "tipo": "conceptual",
    })
    assert r.status_code == 400
    assert r.json()["campo"] == "nivel"


def test_generar_y_responder(client):
    p = client.post("/entrevistas/1/preguntas")
    assert p.status_code == 200
    assert p.json()["pregunta"] == "¿Qué es Python?"

    r = client.post("/entrevistas/1/preguntas/10/respuesta", json={"respuesta": "algo"})
    assert r.status_code == 200
    assert r.json()["puntaje"] == 80


def test_finalizar_incluye_aviso(client):
    r = client.post("/entrevistas/1/finalizar")
    assert r.status_code == 200
    assert "aviso" in r.json()


def test_detalle_inexistente_404(client):
    r = client.get("/entrevistas/404")
    assert r.status_code == 404


def test_historial_y_trazas(client):
    h = client.get("/entrevistas")
    assert h.status_code == 200
    assert h.json()["entrevistas"][0]["puntaje_general"] == 70

    t = client.get("/entrevistas/1/trazas")
    assert t.status_code == 200
    assert t.json()["trazas"][0]["tipo_llamada"] == "pregunta"


def test_fallo_de_ia_devuelve_502(client):
    # Un servicio que lanza AIResponseError debe mapearse a 502 (RNF-06).
    app = create_app()

    class _AIError:
        def generar_siguiente_pregunta(self, entrevista_id):
            raise AIResponseError("IA no devolvió JSON válido")

    app.dependency_overrides[get_service] = lambda: _AIError()
    c = TestClient(app)
    r = c.post("/entrevistas/1/preguntas")
    assert r.status_code == 502
    assert "IA" in r.json()["error"]
