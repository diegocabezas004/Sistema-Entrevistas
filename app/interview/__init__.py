"""Orquestación de la sesión de entrevista (RF-01…RF-10).

Une validación, motores de IA y persistencia en un flujo coherente:
iniciar → generar pregunta → responder/evaluar → finalizar (resumen + plan).
"""

from app.interview.service import InterviewService, interview_service

__all__ = ["InterviewService", "interview_service"]
