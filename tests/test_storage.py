"""Pruebas de persistencia (RF-08, RF-09, RF-10, RNF-05).

Usan una base SQLite temporal (archivo en tmp_path) para no tocar la BD real y
para verificar persistencia entre operaciones. Comprueban el flujo completo:
crear entrevista → guardar preguntas/respuestas/evaluaciones → resumen →
consultar historial y trazabilidad.
"""

from __future__ import annotations

import pytest

from app.ai_client import AICallResult
from app.storage import Database, Repository
from app.validation import InterviewConfig


@pytest.fixture
def repo(tmp_path):
    """Repositorio sobre una BD SQLite temporal."""
    db = Database(path=str(tmp_path / "test.db"))
    return Repository(db=db)


def _config() -> InterviewConfig:
    return InterviewConfig(
        rol="Backend Developer",
        tecnologia="Python",
        nivel="junior",
        idioma="es",
        cantidad_preguntas=2,
        tipo="conceptual",
    )


def _traza(tipo: str) -> AICallResult:
    return AICallResult(
        data={},
        raw_response='{"campo": "valor"}',
        system_prompt=f"system-{tipo}",
        user_prompt=f"user-{tipo}",
        model="claude-haiku-4-5",
        criterios=["claridad"],
    )


def test_crear_entrevista_devuelve_id(repo):
    eid = repo.crear_entrevista(_config())
    assert isinstance(eid, int) and eid > 0


def test_flujo_completo_persiste_y_se_consulta(repo):
    eid = repo.crear_entrevista(_config())

    pid = repo.guardar_pregunta(
        eid, 1, "¿Qué es una variable?", "junior", "Fundamentos",
        ["claridad"], trace=_traza("pregunta"), prompt_version="1.0",
    )
    repo.guardar_respuesta(pid, "Un espacio de memoria con nombre.")
    repo.guardar_evaluacion(
        eid, pid, 85, ["clara"], [], ["no mencionó tipos"],
        "Una variable es...", True, trace=_traza("evaluacion"), prompt_version="1.0",
    )
    repo.guardar_resumen(
        eid, "junior", 85, 85.0, ["fundamentos"], ["tipado"],
        ["Repasar tipos de datos"], trace=_traza("resumen"), prompt_version="1.0",
    )
    repo.completar_entrevista(eid)

    detalle = repo.obtener_entrevista(eid)
    assert detalle is not None
    assert detalle["estado"] == "completada"
    assert len(detalle["preguntas"]) == 1

    pregunta = detalle["preguntas"][0]
    assert pregunta["respuesta"] == "Un espacio de memoria con nombre."
    assert pregunta["evaluacion"]["puntaje"] == 85
    assert pregunta["evaluacion"]["coherente_con_configuracion"] is True
    assert pregunta["criterios"] == ["claridad"]

    assert detalle["resumen"]["nivel_estimado"] == "junior"
    assert detalle["resumen"]["plan_de_estudio"] == ["Repasar tipos de datos"]


def test_trazabilidad_ia_se_guarda_rf10(repo):
    eid = repo.crear_entrevista(_config())
    pid = repo.guardar_pregunta(
        eid, 1, "P", "junior", "T", [], trace=_traza("pregunta"), prompt_version="1.0"
    )
    repo.guardar_evaluacion(
        eid, pid, 70, [], [], [], "mejor", True, trace=_traza("evaluacion")
    )

    trazas = repo.obtener_trazas(eid)
    tipos = {t["tipo_llamada"] for t in trazas}
    assert tipos == {"pregunta", "evaluacion"}
    # Cada traza guarda prompt exacto, respuesta cruda, modelo y criterios.
    p = next(t for t in trazas if t["tipo_llamada"] == "pregunta")
    assert p["system_prompt"] == "system-pregunta"
    assert p["respuesta_cruda"] == '{"campo": "valor"}'
    assert p["modelo"] == "claude-haiku-4-5"
    assert p["criterios"] == ["claridad"]


def test_historial_lista_entrevistas_rf08_rf09(repo):
    e1 = repo.crear_entrevista(_config())
    repo.guardar_resumen(e1, "junior", 60, 60.0, [], [], [])
    e2 = repo.crear_entrevista(_config())
    repo.guardar_resumen(e2, "intermedio", 80, 80.0, [], [], [])

    historial = repo.listar_entrevistas()
    assert len(historial) == 2
    # Trae el puntaje general para comparar avances (RF-09).
    puntajes = {h["id"]: h["puntaje_general"] for h in historial}
    assert puntajes[e1] == 60
    assert puntajes[e2] == 80


def test_obtener_entrevista_inexistente_devuelve_none(repo):
    assert repo.obtener_entrevista(9999) is None
