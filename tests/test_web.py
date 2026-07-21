"""Pruebas de la interfaz web Jinja2 (RNF-07, RF-12).

Se sobreescribe la dependencia del servicio con uno falso, así las tres
pantallas se pueden renderizar sin IA ni base de datos reales. Lo que se
verifica es el flujo (configurar → responder → resultado), la generación
perezosa de preguntas y que un fallo de IA muestre un mensaje en pantalla en
lugar de romper la página.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.ai_client import AIResponseError
from app.api.app import create_app
from app.validation import ValidationError
from app.web import get_service


def _entrevista(preguntas: list[dict], resumen: dict | None = None) -> dict:
    return {
        "id": 1,
        "rol": "Desarrollador Backend",
        "tecnologia": "Python",
        "nivel": "junior",
        "idioma": "es",
        "cantidad_preguntas": 2,
        "tipo": "conceptual",
        "estado": "completada" if resumen else "en_curso",
        "creada_en": "2026-07-21T10:00:00+00:00",
        "preguntas": preguntas,
        "resumen": resumen,
    }


def _pregunta(pid: int, orden: int, respondida: bool = False) -> dict:
    return {
        "id": pid,
        "orden": orden,
        "pregunta": f"¿Qué es una lista en Python? ({orden})",
        "dificultad": "junior",
        "tema": "Estructuras de datos",
        "criterios": ["precisión técnica", "claridad"],
        "respuesta": "Una colección ordenada y mutable." if respondida else None,
        "evaluacion": {
            "puntaje": 75,
            "fortalezas": ["Define bien el concepto"],
            "errores": [],
            "omisiones": ["No menciona la complejidad de acceso"],
            "respuesta_mejorada": "Una lista es una secuencia mutable…",
            "coherente_con_configuracion": True,
        }
        if respondida
        else None,
    }


_RESUMEN = {
    "nivel_estimado": "junior",
    "puntaje_general": 75,
    "promedio_calculado": 75.0,
    "areas_fuertes": ["Fundamentos del lenguaje"],
    "areas_mejora": ["Complejidad algorítmica"],
    "plan_de_estudio": ["Repasar estructuras de datos", "Practicar Big-O"],
}


class _FakeService:
    """Servicio falso con estado mínimo para recorrer el flujo completo."""

    def __init__(self) -> None:
        self.preguntas: list[dict] = []
        self.resumen: dict | None = None
        self.generaciones = 0
        self.respondidas: list[tuple[int, str]] = []

    def iniciar_entrevista(self, config_data):
        if not config_data.get("rol"):
            raise ValidationError("El puesto es obligatorio.", campo="rol")
        return {"entrevista_id": 1, "config": config_data}

    def generar_siguiente_pregunta(self, entrevista_id):
        self.generaciones += 1
        orden = len(self.preguntas) + 1
        self.preguntas.append(_pregunta(10 + orden, orden))
        return {"pregunta_id": 10 + orden, "orden": orden, "total": 2}

    def responder_pregunta(self, entrevista_id, pregunta_id, respuesta):
        self.respondidas.append((pregunta_id, respuesta))
        for p in self.preguntas:
            if p["id"] == pregunta_id:
                p.update(_pregunta(pregunta_id, p["orden"], respondida=True))
        return {"pregunta_id": pregunta_id, "puntaje": 75}

    def finalizar_entrevista(self, entrevista_id):
        self.resumen = _RESUMEN
        return {"entrevista_id": entrevista_id, **_RESUMEN}

    def obtener_entrevista(self, entrevista_id):
        if entrevista_id == 404:
            return None
        return _entrevista(self.preguntas, self.resumen)

    def listar_historial(self):
        return [
            {
                "id": 1,
                "rol": "Desarrollador Backend",
                "tecnologia": "Python",
                "nivel": "junior",
                "tipo": "conceptual",
                "estado": "completada",
                "creada_en": "2026-07-21T10:00:00+00:00",
                "puntaje_general": 75,
            }
        ]

    def obtener_trazas(self, entrevista_id):
        return []


@pytest.fixture
def fake() -> _FakeService:
    return _FakeService()


@pytest.fixture
def client(fake: _FakeService) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_service] = lambda: fake
    return TestClient(app)


# ------------------------- Pantalla 1: configurar ------------------------- #

def test_raiz_redirige_a_la_interfaz(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "/ui"


def test_configurar_muestra_formulario_historial_y_aviso(client):
    r = client.get("/ui")
    assert r.status_code == 200
    cuerpo = r.text
    assert 'action="/ui/entrevistas"' in cuerpo
    assert "Entrevista junior" in cuerpo          # escenarios de la sección 7
    assert "Sesiones anteriores" in cuerpo        # historial (RF-08/RF-09)
    assert "herramienta de práctica" in cuerpo    # disclaimer (§12)


def test_crear_entrevista_redirige_a_la_sesion(client):
    r = client.post(
        "/ui/entrevistas",
        data={
            "rol": "Desarrollador Backend",
            "tecnologia": "Python",
            "nivel": "junior",
            "idioma": "es",
            "cantidad_preguntas": "2",
            "tipo": "conceptual",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/ui/entrevistas/1"


def test_configuracion_invalida_vuelve_con_mensaje(client):
    r = client.post(
        "/ui/entrevistas",
        data={
            "rol": "",
            "tecnologia": "Python",
            "nivel": "junior",
            "idioma": "es",
            "cantidad_preguntas": "2",
            "tipo": "conceptual",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert "El puesto es obligatorio." in r.text


# ------------------------- Pantalla 2: responder -------------------------- #

def test_entrar_a_la_sesion_genera_la_pregunta(client, fake):
    r = client.get("/ui/entrevistas/1")
    assert r.status_code == 200
    assert fake.generaciones == 1
    assert "¿Qué es una lista en Python? (1)" in r.text
    assert "Pregunta 1 de 2" in r.text


def test_no_regenera_si_ya_hay_pregunta_abierta(client, fake):
    client.get("/ui/entrevistas/1")
    client.get("/ui/entrevistas/1")
    assert fake.generaciones == 1  # recargar no consume otra llamada a la IA


def test_responder_evalua_y_muestra_retroalimentacion(client, fake):
    client.get("/ui/entrevistas/1")
    r = client.post(
        "/ui/entrevistas/1/preguntas/11/respuesta",
        data={"respuesta": "Una colección ordenada y mutable."},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert fake.respondidas == [(11, "Una colección ordenada y mutable.")]

    pantalla = client.get("/ui/entrevistas/1").text
    assert "Retroalimentación de la pregunta 1" in pantalla
    assert "No menciona la complejidad de acceso" in pantalla


def test_sesion_completa_redirige_al_resultado(client, fake):
    fake.preguntas = [_pregunta(11, 1, True), _pregunta(12, 2, True)]
    r = client.get("/ui/entrevistas/1", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/ui/entrevistas/1/resultado"


def test_entrevista_inexistente_vuelve_al_inicio(client):
    r = client.get("/ui/entrevistas/404", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"].startswith("/ui?e=")


# ------------------------- Pantalla 3: resultado -------------------------- #

def test_resultado_finaliza_y_muestra_plan(client, fake):
    fake.preguntas = [_pregunta(11, 1, True), _pregunta(12, 2, True)]
    r = client.get("/ui/entrevistas/1/resultado")
    assert r.status_code == 200
    cuerpo = r.text
    assert "Repasar estructuras de datos" in cuerpo   # plan de mejora (RF-07)
    assert "Fundamentos del lenguaje" in cuerpo       # áreas fuertes (RF-06)
    assert "Complejidad algorítmica" in cuerpo        # áreas de mejora (RF-06)
    assert "Pregunta por pregunta" in cuerpo


def test_resultado_no_refinaliza_si_ya_hay_resumen(client, fake):
    fake.preguntas = [_pregunta(11, 1, True)]
    client.get("/ui/entrevistas/1/resultado")
    llamadas = fake.resumen
    client.get("/ui/entrevistas/1/resultado")
    assert llamadas is fake.resumen


# ------------------------- Errores de IA (RF-12) -------------------------- #

def test_fallo_de_ia_al_generar_muestra_mensaje_en_pantalla(client, fake):
    def _falla(_entrevista_id):
        raise AIResponseError("la IA no devolvió JSON válido")

    fake.generar_siguiente_pregunta = _falla
    r = client.get("/ui/entrevistas/1")
    assert r.status_code == 200  # la página no se rompe
    assert "no devolvió una respuesta utilizable" in r.text


def test_fallo_de_ia_al_evaluar_vuelve_con_mensaje(client, fake):
    client.get("/ui/entrevistas/1")

    def _falla(*_args):
        raise AIResponseError("respuesta incompleta")

    fake.responder_pregunta = _falla
    r = client.post(
        "/ui/entrevistas/1/preguntas/11/respuesta",
        data={"respuesta": "algo"},
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert "no devolvió una respuesta utilizable" in r.text
