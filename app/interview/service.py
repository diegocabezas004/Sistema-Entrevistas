"""Orquestación de la sesión de entrevista (RF-01…RF-08).

Une todos los módulos y define el flujo:

    iniciar → generar pregunta → responder (evaluar) → ... → finalizar (resumen)

La base de datos es la única fuente de verdad del estado (no se guarda estado en
memoria), así el flujo es robusto ante reinicios. Cada paso valida, llama a la IA
por sus motores y persiste con trazabilidad.
"""

from __future__ import annotations

from typing import Any

from app.evaluation_engine import (
    EvaluationEngine,
    evaluation_engine as default_evaluation_engine,
)
from app.evaluation_engine.prompts import PROMPT_EVALUACION_VERSION
from app.feedback import FeedbackEngine, feedback_engine as default_feedback_engine
from app.feedback.prompts import PROMPT_RESUMEN_VERSION
from app.questions_engine import (
    QuestionsEngine,
    questions_engine as default_questions_engine,
)
from app.questions_engine.prompts import PROMPT_PREGUNTA_VERSION
from app.storage import Repository, repository as default_repository
from app.validation import InterviewConfig, ValidationError, validar_config


def _config_desde_fila(fila: dict[str, Any]) -> InterviewConfig:
    """Reconstruye un InterviewConfig desde una fila de la tabla entrevistas.

    Los valores ya están normalizados (se validaron al crear la entrevista), por
    eso se construye el dataclass directamente.
    """
    return InterviewConfig(
        rol=fila["rol"],
        tecnologia=fila["tecnologia"],
        nivel=fila["nivel"],
        idioma=fila["idioma"],
        cantidad_preguntas=fila["cantidad_preguntas"],
        tipo=fila["tipo"],
    )


class InterviewService:
    """Coordina el ciclo de vida completo de una entrevista."""

    def __init__(
        self,
        repo: Repository | None = None,
        questions: QuestionsEngine | None = None,
        evaluations: EvaluationEngine | None = None,
        feedback: FeedbackEngine | None = None,
    ) -> None:
        # Inyección de dependencias: en pruebas se pasan motores simulados.
        self._repo = repo or default_repository
        self._questions = questions or default_questions_engine
        self._evaluations = evaluations or default_evaluation_engine
        self._feedback = feedback or default_feedback_engine

    # ------------------------------------------------------------------ #
    # 1. Iniciar (RF-01)
    # ------------------------------------------------------------------ #
    def iniciar_entrevista(self, config_data: dict[str, Any]) -> dict[str, Any]:
        """Valida la configuración y crea la entrevista.

        Returns:
            dict con 'entrevista_id' y la configuración normalizada.

        Raises:
            ValidationError: si la configuración es inválida (RNF-04).
        """
        config = validar_config(config_data)  # RF-01 / RNF-04
        entrevista_id = self._repo.crear_entrevista(config)
        return {
            "entrevista_id": entrevista_id,
            "config": {
                "rol": config.rol,
                "tecnologia": config.tecnologia,
                "nivel": config.nivel,
                "idioma": config.idioma,
                "cantidad_preguntas": config.cantidad_preguntas,
                "tipo": config.tipo,
            },
        }

    # ------------------------------------------------------------------ #
    # 2. Generar siguiente pregunta (RF-02)
    # ------------------------------------------------------------------ #
    def generar_siguiente_pregunta(self, entrevista_id: int) -> dict[str, Any]:
        """Genera y guarda la siguiente pregunta de la entrevista.

        Respeta la cantidad configurada y pasa las preguntas previas a la IA para
        evitar repeticiones (RF-02).

        Raises:
            ValidationError: si la entrevista no existe o ya se alcanzó el total.
            AIResponseError: si la IA falla.
        """
        detalle = self._repo.obtener_entrevista(entrevista_id)
        if detalle is None:
            raise ValidationError("La entrevista no existe.", campo="entrevista_id")

        config = _config_desde_fila(detalle)
        previas = [p["pregunta"] for p in detalle["preguntas"]]

        if len(previas) >= config.cantidad_preguntas:
            raise ValidationError(
                "Ya se generaron todas las preguntas de esta entrevista.",
                campo="entrevista_id",
            )

        pregunta = self._questions.generar_pregunta(config, preguntas_previas=previas)
        orden = len(previas) + 1
        pregunta_id = self._repo.guardar_pregunta(
            entrevista_id,
            orden,
            pregunta.pregunta,
            pregunta.dificultad,
            pregunta.tema,
            pregunta.criterios_evaluados,
            trace=pregunta.trace,
            prompt_version=PROMPT_PREGUNTA_VERSION,
        )
        return {
            "pregunta_id": pregunta_id,
            "orden": orden,
            "total": config.cantidad_preguntas,
            **pregunta.resumen(),
        }

    # ------------------------------------------------------------------ #
    # 3. Responder y evaluar (RF-03, RF-04, RF-05)
    # ------------------------------------------------------------------ #
    def responder_pregunta(
        self, entrevista_id: int, pregunta_id: int, respuesta: str
    ) -> dict[str, Any]:
        """Guarda la respuesta del usuario y la evalúa con IA.

        Raises:
            ValidationError: si la entrevista/pregunta no existe o la respuesta
                es inválida (RNF-04).
            AIResponseError: si la IA falla.
        """
        detalle = self._repo.obtener_entrevista(entrevista_id)
        if detalle is None:
            raise ValidationError("La entrevista no existe.", campo="entrevista_id")

        config = _config_desde_fila(detalle)
        pregunta = next(
            (p for p in detalle["preguntas"] if p["id"] == pregunta_id), None
        )
        if pregunta is None:
            raise ValidationError(
                "La pregunta no pertenece a esta entrevista.", campo="pregunta_id"
            )

        # Guardar la respuesta (RF-03). validar_respuesta se ejecuta dentro del
        # motor de evaluación, pero también aquí antes de persistir.
        from app.validation import validar_respuesta

        texto = validar_respuesta(respuesta)
        self._repo.guardar_respuesta(pregunta_id, texto)

        # Evaluar (RF-04/RF-05).
        evaluacion = self._evaluations.evaluar_respuesta(
            config,
            pregunta["pregunta"],
            texto,
            criterios=pregunta["criterios"],
        )
        self._repo.guardar_evaluacion(
            entrevista_id,
            pregunta_id,
            evaluacion.puntaje,
            evaluacion.fortalezas,
            evaluacion.errores,
            evaluacion.omisiones,
            evaluacion.respuesta_mejorada,
            evaluacion.coherente_con_configuracion,
            trace=evaluacion.trace,
            prompt_version=PROMPT_EVALUACION_VERSION,
        )
        return {"pregunta_id": pregunta_id, **evaluacion.resumen()}

    # ------------------------------------------------------------------ #
    # 4. Finalizar: resumen + plan de mejora (RF-06, RF-07, RF-08)
    # ------------------------------------------------------------------ #
    def finalizar_entrevista(self, entrevista_id: int) -> dict[str, Any]:
        """Genera el resumen final, lo guarda y marca la entrevista completada.

        Raises:
            ValidationError: si la entrevista no existe o no tiene respuestas
                evaluadas (RNF-04).
            AIResponseError: si la IA falla.
        """
        detalle = self._repo.obtener_entrevista(entrevista_id)
        if detalle is None:
            raise ValidationError("La entrevista no existe.", campo="entrevista_id")

        config = _config_desde_fila(detalle)

        # Reunir las evaluaciones para el resumen.
        items = []
        for p in detalle["preguntas"]:
            ev = p.get("evaluacion")
            if ev is None:
                continue
            items.append(
                {
                    "pregunta": p["pregunta"],
                    "tema": p["tema"],
                    "puntaje": ev["puntaje"],
                    "fortalezas": ev["fortalezas"],
                    "errores": ev["errores"],
                    "omisiones": ev["omisiones"],
                }
            )

        # Defensa en profundidad (RNF-04): no finalizar sin respuestas evaluadas,
        # sin depender de que el motor de feedback lo verifique.
        if not items:
            raise ValidationError(
                "No se puede finalizar: la entrevista no tiene respuestas evaluadas.",
                campo="entrevista_id",
            )

        resumen = self._feedback.generar_resumen(config, items)  # valida vacío (RNF-04)
        self._repo.guardar_resumen(
            entrevista_id,
            resumen.nivel_estimado,
            resumen.puntaje_general,
            resumen.promedio_calculado,
            resumen.areas_fuertes,
            resumen.areas_mejora,
            resumen.plan_de_estudio,
            trace=resumen.trace,
            prompt_version=PROMPT_RESUMEN_VERSION,
        )
        self._repo.completar_entrevista(entrevista_id)
        return {"entrevista_id": entrevista_id, **resumen.resumen()}

    # ------------------------------------------------------------------ #
    # 5. Consultas (RF-08, RF-09, RF-10)
    # ------------------------------------------------------------------ #
    def obtener_entrevista(self, entrevista_id: int) -> dict[str, Any] | None:
        """Detalle completo de una entrevista (RF-08)."""
        return self._repo.obtener_entrevista(entrevista_id)

    def listar_historial(self) -> list[dict[str, Any]]:
        """Historial de entrevistas para ver avances (RF-08/RF-09)."""
        return self._repo.listar_entrevistas()

    def obtener_trazas(self, entrevista_id: int) -> list[dict[str, Any]]:
        """Trazabilidad de IA de una entrevista (RF-10/RNF-05)."""
        return self._repo.obtener_trazas(entrevista_id)


# Instancia compartida lista para usar.
interview_service = InterviewService()
