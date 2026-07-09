# Documentación Funcional

## 1. Problema que resuelve

Prepararse para entrevistas técnicas es difícil sin práctica realista y retroalimentación. Los bancos de preguntas fijas no se adaptan al rol, nivel ni tecnología, y no evalúan las respuestas ni orientan sobre qué mejorar.

El **Simulador Generativo de Entrevistas Técnicas** ofrece una práctica personalizada: la IA genera preguntas nuevas según la configuración del usuario, evalúa cada respuesta con criterio profesional, entrega retroalimentación estructurada y propone un plan de mejora basado en el desempeño real.

> **Importante:** es una herramienta de **práctica**, no una certificación oficial ni una garantía de contratación.

## 2. Usuarios

- **Estudiantes** que se preparan para entrevistas técnicas.
- **Profesionales** que quieren repasar o cambiar de rol/tecnología.
- **Docentes** que quieren una herramienta de práctica para sus alumnos.

Los perfiles son ficticios/académicos; no se piden datos personales sensibles (RNF-03).

## 3. Funcionalidades

| # | Funcionalidad | Descripción |
|---|---|---|
| RF-01 | Configuración de entrevista | El usuario define rol, tecnología, nivel, idioma, cantidad de preguntas y tipo. |
| RF-02 | Generación de preguntas | La IA genera preguntas nuevas y contextualizadas; no repite dentro de la sesión. |
| RF-03 | Registro de respuestas | El usuario responde cada pregunta; queda asociada a la entrevista. |
| RF-04 | Evaluación generativa | La IA evalúa precisión técnica, claridad, profundidad, estructura y riesgo de conceptos incorrectos. |
| RF-05 | Retroalimentación individual | Por pregunta: fortalezas, errores, omisiones y una respuesta mejorada. |
| RF-06 | Resultado general | Puntaje agregado, nivel estimado, áreas fuertes y áreas de mejora. |
| RF-07 | Plan de mejora | Ruta de estudio/práctica breve basada en el desempeño real. |
| RF-08 | Historial | Toda entrevista completada queda guardada y consultable. |
| RF-09 | Comparación de avances | El usuario ve entrevistas anteriores y su puntaje para detectar avances. |
| RF-10 | Trazabilidad de IA | Se guarda prompt exacto, respuesta cruda, criterios y fecha/hora de cada llamada. |
| RF-11 | Validación de coherencia | El sistema detecta si una pregunta/evaluación no corresponde al rol/nivel/tecnología. |
| RF-12 | Manejo de errores | Fallos de IA, datos faltantes o formato inválido no rompen el flujo. |

## 4. Flujo de uso (paso a paso)

1. **Configurar la entrevista** (RF-01): rol, tecnología, nivel, idioma, cantidad de preguntas y tipo.
2. **Generar una pregunta** (RF-02): la IA propone una pregunta acorde a la configuración.
3. **Responder** (RF-03): el usuario escribe su respuesta.
4. **Recibir evaluación** (RF-04/RF-05): la IA devuelve puntaje, fortalezas, errores, omisiones y una respuesta mejorada.
5. Repetir 2–4 hasta completar la cantidad de preguntas configurada.
6. **Finalizar** (RF-06/RF-07): la IA entrega el resultado general y el plan de mejora.
7. **Consultar historial** (RF-08/RF-09): revisar entrevistas pasadas y comparar avances.

## 5. Entradas

| Entrada | Ejemplo |
|---|---|
| Rol | "Backend Developer" |
| Tecnología | "Python" |
| Nivel | junior / intermedio / senior |
| Idioma | es / en |
| Cantidad de preguntas | 1 a 20 |
| Tipo | técnica, conceptual, práctica, situacional, arquitectura, mixta |
| Respuesta del usuario | texto libre |

## 6. Salidas

| Salida | Contenido |
|---|---|
| Pregunta | enunciado, dificultad, criterios evaluados, tema |
| Evaluación | puntaje (0–100), fortalezas, errores, omisiones, respuesta mejorada, coherencia |
| Resumen | nivel estimado, puntaje general, promedio calculado, áreas fuertes, áreas de mejora, plan de estudio |
| Trazabilidad | prompts, respuestas crudas, modelo, criterios, fecha/hora |

## 7. Tipos de entrevista

| Tipo | Enfoque |
|---|---|
| Técnica | Conocimiento técnico aplicado. |
| Conceptual | Fundamentos y teoría. |
| Práctica | Problemas o resolución de código. |
| Situacional | Situaciones reales de trabajo. |
| Arquitectura | Diseño o arquitectura básica. |
| Mixta | Combinación de las anteriores. |

## 8. Restricciones

- La evaluación es de práctica; **no** es certificación oficial ni garantiza contratación.
- No se afirma que el usuario aprobará una entrevista real.
- No se piden datos personales sensibles.
- El alcance no incluye audio/video, integración con plataformas de reclutamiento, ni entrenamiento de modelos propios.

## 9. Reglas de negocio destacadas

- No se puede iniciar una entrevista con configuración vacía o inválida.
- No se puede responder con texto vacío.
- No se generan más preguntas que las configuradas.
- No se puede finalizar una entrevista sin respuestas evaluadas.
- Si la IA genera una pregunta cuyo nivel no coincide con el configurado, se detecta como incoherencia (RF-11).
