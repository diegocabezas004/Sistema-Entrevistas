# Evidencia Individual

> **Plantilla para la defensa individual (30%).** Cada integrante debe poder explicar su parte, responder preguntas técnicas sobre el flujo de IA y mostrar evidencia real de participación (código, pruebas, documentación, commits por rama/módulo). Completa las secciones con tu nombre y tu aporte concreto.

---

## Cómo usar esta plantilla

1. Cada integrante llena su sección con: módulos/funcionalidades de los que fue responsable, archivos y pruebas asociadas, y qué puede explicar en la defensa.
2. Asegúrate de que tus commits estén asociados a tu autoría (rama o co-autoría).
3. Prepárate para explicar **el flujo de IA** de tu parte: qué prompt se usa, qué valida, cómo se persiste y cómo se manejan los errores.

---

## Sugerencia de reparto por módulos

El proyecto tiene 8 módulos que pueden distribuirse. Ajusten según el tamaño del equipo:

| Área | Módulos / Archivos | Requisitos |
|---|---|---|
| Integración con IA | `app/ai_client/` | RF-10, RF-12, RNF-02, RNF-05 |
| Validación | `app/validation/` | RF-11, RF-12, RNF-04 |
| Generación de preguntas | `app/questions_engine/` | RF-02 |
| Evaluación | `app/evaluation_engine/` | RF-04, RF-05 |
| Retroalimentación | `app/feedback/` | RF-06, RF-07 |
| Persistencia | `app/storage/` | RF-08, RF-09, RF-10 |
| Orquestación | `app/interview/` | RF-01…RF-08 |
| API REST | `app/api/`, `app/main.py` | RF-12, RNF-06, RNF-07 |
| Documentación | `/docs`, `README.md` | Sección 9 rúbrica |

---

## Integrante 1 — [Nombre completo]

- **Rol / responsabilidad:** [p. ej. Integración con IA y validación]
- **Módulos/archivos:** [p. ej. `app/ai_client/`, `app/validation/`]
- **Funcionalidades implementadas:** [RF-xx, RF-yy]
- **Pruebas asociadas:** [p. ej. `tests/test_ai_client.py`, `tests/test_validation.py`]
- **Qué puedo explicar en la defensa:**
  - [p. ej. cómo `ai_client` fuerza JSON, valida campos y reintenta]
  - [p. ej. cómo se valida la coherencia RF-11]
- **Evidencia (commits/ramas):** [enlaces o hashes]

---

## Integrante 2 — [Nombre completo]

- **Rol / responsabilidad:**
- **Módulos/archivos:**
- **Funcionalidades implementadas:**
- **Pruebas asociadas:**
- **Qué puedo explicar en la defensa:**
- **Evidencia (commits/ramas):**

---

## Integrante 3 — [Nombre completo]

- **Rol / responsabilidad:**
- **Módulos/archivos:**
- **Funcionalidades implementadas:**
- **Pruebas asociadas:**
- **Qué puedo explicar en la defensa:**
- **Evidencia (commits/ramas):**

---

## Integrante 4 — [Nombre completo]

- **Rol / responsabilidad:**
- **Módulos/archivos:**
- **Funcionalidades implementadas:**
- **Pruebas asociadas:**
- **Qué puedo explicar en la defensa:**
- **Evidencia (commits/ramas):**

---

## Preguntas de defensa que conviene practicar

- ¿Por qué solo `ai_client` habla con la API de Anthropic? ¿Qué ventaja da?
- ¿Cómo se garantiza que la IA no repita preguntas (RF-02)?
- ¿Qué pasa si la IA devuelve un JSON inválido? (reintento + error controlado)
- ¿Cómo se detecta que una pregunta no corresponde al nivel configurado (RF-11)?
- ¿Dónde y cómo se guarda la trazabilidad de cada llamada a la IA (RF-10)?
- ¿Cómo se mapean los errores de negocio a códigos HTTP (RNF-06)?
- ¿Por qué se calcula un promedio local además del puntaje que da la IA?
- ¿Cómo se asegura que la API key nunca esté en el código (RNF-02)?
