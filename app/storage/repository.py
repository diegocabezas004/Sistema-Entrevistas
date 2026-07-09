"""Repositorio: operaciones de persistencia sobre la base de datos.

Expone una API en español orientada al flujo de la entrevista. Cada método que
guarda contenido generado por IA registra también su traza (RF-10/RNF-05).

El repositorio recibe datos ya validados (por `validation`) y objetos de
trazabilidad (`AICallResult` del `ai_client`); no habla con la IA ni valida
reglas de negocio: solo persiste y consulta.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Sequence

from app.ai_client import AICallResult
from app.storage.db import Database, database as default_database
from app.validation import InterviewConfig


def _ahora() -> str:
    """Fecha/hora actual en ISO 8601 UTC (para trazabilidad, RNF-05)."""
    return datetime.now(timezone.utc).isoformat()


def _json_lista(valor: Sequence[str] | None) -> str:
    """Serializa una lista de textos a JSON para guardarla en una columna TEXT."""
    return json.dumps(list(valor or []), ensure_ascii=False)


def _leer_lista(valor: str | None) -> list[str]:
    """Deserializa una columna JSON a lista de textos (tolerante a nulos)."""
    if not valor:
        return []
    try:
        data = json.loads(valor)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


class Repository:
    """Acceso a datos de entrevistas, con trazabilidad de IA."""

    def __init__(self, db: Database | None = None) -> None:
        self._db = db or default_database

    # ------------------------------------------------------------------ #
    # Entrevista (RF-01 / RF-08)
    # ------------------------------------------------------------------ #
    def crear_entrevista(self, config: InterviewConfig) -> int:
        """Crea una entrevista en estado 'en_curso' y devuelve su id."""
        with self._db.connect() as conn:
            cur = conn.execute(
                """INSERT INTO entrevistas
                   (rol, tecnologia, nivel, idioma, cantidad_preguntas, tipo,
                    estado, creada_en)
                   VALUES (?, ?, ?, ?, ?, ?, 'en_curso', ?)""",
                (
                    config.rol,
                    config.tecnologia,
                    config.nivel,
                    config.idioma,
                    config.cantidad_preguntas,
                    config.tipo,
                    _ahora(),
                ),
            )
            return int(cur.lastrowid)

    def completar_entrevista(self, entrevista_id: int) -> None:
        """Marca una entrevista como completada (RF-08)."""
        with self._db.connect() as conn:
            conn.execute(
                "UPDATE entrevistas SET estado='completada', completada_en=? WHERE id=?",
                (_ahora(), entrevista_id),
            )

    # ------------------------------------------------------------------ #
    # Preguntas, respuestas, evaluaciones
    # ------------------------------------------------------------------ #
    def guardar_pregunta(
        self,
        entrevista_id: int,
        orden: int,
        pregunta: str,
        dificultad: str,
        tema: str,
        criterios: Sequence[str],
        trace: AICallResult | None = None,
        prompt_version: str | None = None,
    ) -> int:
        """Guarda una pregunta y su traza de IA (RF-03/RF-10)."""
        with self._db.connect() as conn:
            cur = conn.execute(
                """INSERT INTO preguntas
                   (entrevista_id, orden, pregunta, dificultad, tema, criterios,
                    creada_en)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    entrevista_id,
                    orden,
                    pregunta,
                    dificultad,
                    tema,
                    _json_lista(criterios),
                    _ahora(),
                ),
            )
            pregunta_id = int(cur.lastrowid)
            if trace is not None:
                self._guardar_traza(
                    conn, "pregunta", trace, prompt_version,
                    entrevista_id=entrevista_id, pregunta_id=pregunta_id,
                )
            return pregunta_id

    def guardar_respuesta(self, pregunta_id: int, texto: str) -> int:
        """Guarda la respuesta del usuario a una pregunta (RF-03)."""
        with self._db.connect() as conn:
            cur = conn.execute(
                "INSERT INTO respuestas (pregunta_id, texto, creada_en) VALUES (?, ?, ?)",
                (pregunta_id, texto, _ahora()),
            )
            return int(cur.lastrowid)

    def guardar_evaluacion(
        self,
        entrevista_id: int,
        pregunta_id: int,
        puntaje: int,
        fortalezas: Sequence[str],
        errores: Sequence[str],
        omisiones: Sequence[str],
        respuesta_mejorada: str,
        coherente_con_configuracion: bool,
        trace: AICallResult | None = None,
        prompt_version: str | None = None,
    ) -> int:
        """Guarda la evaluación de una respuesta y su traza de IA (RF-04/RF-10)."""
        with self._db.connect() as conn:
            cur = conn.execute(
                """INSERT INTO evaluaciones
                   (pregunta_id, puntaje, fortalezas, errores, omisiones,
                    respuesta_mejorada, coherente_con_configuracion, creada_en)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    pregunta_id,
                    puntaje,
                    _json_lista(fortalezas),
                    _json_lista(errores),
                    _json_lista(omisiones),
                    respuesta_mejorada,
                    1 if coherente_con_configuracion else 0,
                    _ahora(),
                ),
            )
            evaluacion_id = int(cur.lastrowid)
            if trace is not None:
                self._guardar_traza(
                    conn, "evaluacion", trace, prompt_version,
                    entrevista_id=entrevista_id, pregunta_id=pregunta_id,
                )
            return evaluacion_id

    def guardar_resumen(
        self,
        entrevista_id: int,
        nivel_estimado: str,
        puntaje_general: int,
        promedio_calculado: float,
        areas_fuertes: Sequence[str],
        areas_mejora: Sequence[str],
        plan_de_estudio: Sequence[str],
        trace: AICallResult | None = None,
        prompt_version: str | None = None,
    ) -> int:
        """Guarda el resumen final y su traza de IA (RF-06/RF-07/RF-10)."""
        with self._db.connect() as conn:
            cur = conn.execute(
                """INSERT INTO resumenes
                   (entrevista_id, nivel_estimado, puntaje_general,
                    promedio_calculado, areas_fuertes, areas_mejora,
                    plan_de_estudio, creado_en)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    entrevista_id,
                    nivel_estimado,
                    puntaje_general,
                    promedio_calculado,
                    _json_lista(areas_fuertes),
                    _json_lista(areas_mejora),
                    _json_lista(plan_de_estudio),
                    _ahora(),
                ),
            )
            resumen_id = int(cur.lastrowid)
            if trace is not None:
                self._guardar_traza(
                    conn, "resumen", trace, prompt_version,
                    entrevista_id=entrevista_id,
                )
            return resumen_id

    # ------------------------------------------------------------------ #
    # Consultas (RF-08 historial / RF-09 comparación)
    # ------------------------------------------------------------------ #
    def listar_entrevistas(self) -> list[dict[str, Any]]:
        """Lista todas las entrevistas con su puntaje (para historial y avances)."""
        with self._db.connect() as conn:
            filas = conn.execute(
                """SELECT e.*, r.puntaje_general, r.nivel_estimado,
                          r.promedio_calculado
                   FROM entrevistas e
                   LEFT JOIN resumenes r ON r.entrevista_id = e.id
                   ORDER BY e.creada_en DESC"""
            ).fetchall()
            return [dict(f) for f in filas]

    def obtener_entrevista(self, entrevista_id: int) -> dict[str, Any] | None:
        """Devuelve el detalle completo de una entrevista (RF-08).

        Incluye preguntas, respuestas, evaluaciones y el resumen final.
        """
        with self._db.connect() as conn:
            ent = conn.execute(
                "SELECT * FROM entrevistas WHERE id=?", (entrevista_id,)
            ).fetchone()
            if ent is None:
                return None

            detalle: dict[str, Any] = dict(ent)
            detalle["preguntas"] = self._preguntas_con_detalle(conn, entrevista_id)

            resumen = conn.execute(
                "SELECT * FROM resumenes WHERE entrevista_id=? ORDER BY id DESC LIMIT 1",
                (entrevista_id,),
            ).fetchone()
            detalle["resumen"] = self._formatear_resumen(resumen) if resumen else None
            return detalle

    def obtener_trazas(self, entrevista_id: int) -> list[dict[str, Any]]:
        """Devuelve todas las trazas de IA de una entrevista (RF-10/RNF-05)."""
        with self._db.connect() as conn:
            filas = conn.execute(
                "SELECT * FROM ia_trazas WHERE entrevista_id=? ORDER BY id",
                (entrevista_id,),
            ).fetchall()
            resultado = []
            for f in filas:
                d = dict(f)
                d["criterios"] = _leer_lista(d["criterios"])
                resultado.append(d)
            return resultado

    # ------------------------------------------------------------------ #
    # Internos
    # ------------------------------------------------------------------ #
    @staticmethod
    def _guardar_traza(
        conn,
        tipo_llamada: str,
        trace: AICallResult,
        prompt_version: str | None,
        entrevista_id: int | None = None,
        pregunta_id: int | None = None,
    ) -> None:
        """Inserta una traza de IA (prompt, respuesta cruda, modelo, criterios)."""
        conn.execute(
            """INSERT INTO ia_trazas
               (entrevista_id, pregunta_id, tipo_llamada, system_prompt,
                user_prompt, respuesta_cruda, modelo, criterios, prompt_version,
                creada_en)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entrevista_id,
                pregunta_id,
                tipo_llamada,
                trace.system_prompt,
                trace.user_prompt,
                trace.raw_response,
                trace.model,
                _json_lista(trace.criterios),
                prompt_version,
                trace.timestamp,
            ),
        )

    def _preguntas_con_detalle(self, conn, entrevista_id: int) -> list[dict[str, Any]]:
        """Ensambla cada pregunta con su respuesta y evaluación."""
        preguntas = conn.execute(
            "SELECT * FROM preguntas WHERE entrevista_id=? ORDER BY orden",
            (entrevista_id,),
        ).fetchall()

        detalle = []
        for p in preguntas:
            pd = dict(p)
            pd["criterios"] = _leer_lista(pd["criterios"])

            respuesta = conn.execute(
                "SELECT * FROM respuestas WHERE pregunta_id=? ORDER BY id DESC LIMIT 1",
                (p["id"],),
            ).fetchone()
            pd["respuesta"] = respuesta["texto"] if respuesta else None

            ev = conn.execute(
                "SELECT * FROM evaluaciones WHERE pregunta_id=? ORDER BY id DESC LIMIT 1",
                (p["id"],),
            ).fetchone()
            pd["evaluacion"] = self._formatear_evaluacion(ev) if ev else None

            detalle.append(pd)
        return detalle

    @staticmethod
    def _formatear_evaluacion(ev) -> dict[str, Any]:
        d = dict(ev)
        d["fortalezas"] = _leer_lista(d["fortalezas"])
        d["errores"] = _leer_lista(d["errores"])
        d["omisiones"] = _leer_lista(d["omisiones"])
        d["coherente_con_configuracion"] = bool(d["coherente_con_configuracion"])
        return d

    @staticmethod
    def _formatear_resumen(r) -> dict[str, Any]:
        d = dict(r)
        d["areas_fuertes"] = _leer_lista(d["areas_fuertes"])
        d["areas_mejora"] = _leer_lista(d["areas_mejora"])
        d["plan_de_estudio"] = _leer_lista(d["plan_de_estudio"])
        return d


# Instancia compartida lista para usar.
repository = Repository()
