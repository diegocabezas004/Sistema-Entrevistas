# Bitácora del chat — Desarrollo del proyecto

> Registro cronológico de la conversación con Claude Code durante la construcción del proyecto. Cada entrada resume lo que pidió el usuario y lo que se hizo en respuesta. Sirve como memoria del proceso para retomar o repasar.

---

## Turno 1 — "lee el CLAUDE.md papasito"

**Usuario:** pidió leer el `CLAUDE.md` del proyecto.

**Se hizo:**
- Se leyó y resumió el `CLAUDE.md`: objetivo (simulador de entrevistas con IA central), stack (Python + FastAPI, SQLite/PostgreSQL, Anthropic Claude), arquitectura modular obligatoria, los 12 RF y 8 RNF, los 3 prompts obligatorios, restricciones éticas y documentación exigida.
- Se confirmó el orden de implementación de la §11 y las reglas duras (una sola capa de IA, API key solo por `.env`, nunca prometer contratación).
- Se propuso arrancar por el scaffolding + `ai_client`.

---

## Turno 2 — "si, demosle... quiero que lo hagas con sqlite"

**Usuario:** dio luz verde y eligió SQLite.

**Se hizo (scaffolding + `ai_client`):**
- Se inspeccionó el estado inicial (proyecto casi vacío, `venv` vacío, `.env`/`.gitignore` vacíos).
- Estructura de carpetas: `app/` con los 8 submódulos, `tests/`, `docs/`.
- `.gitignore` (protege `.env`, `*.db`, `venv/`), `.env.example` (con `claude-haiku-4-5` y `DATABASE_URL` SQLite), `requirements.txt`.
- `app/config.py`: configuración central por variables de entorno.
- Se consultó la referencia oficial de la API de Claude para usar el SDK correctamente.
- Módulo **`ai_client`** (`client.py`, `errors.py`): única capa que habla con Anthropic; `generate_json()` con system prompt base ético, JSON forzado, validación de campos, reintento y trazabilidad (`AICallResult`).
- Se recreó el `venv` (estaba vacío) e instalaron dependencias.
- Pruebas `tests/test_ai_client.py` (5) — **todas verdes**.

---

## Turno 3 — "dale amor" (continuar)

**Usuario:** pidió seguir.

**Se hizo (módulo `validation`):**
- `constants.py` (catálogos: niveles, tipos, idiomas, rangos), `errors.py` (`ValidationError` con campo), `validators.py`.
- Normalización tolerante (acentos/sinónimos), validación de config, respuestas, puntajes (0–100), y estructura/coherencia de las 3 salidas de IA.
- Coherencia RF-11: dificultad de la pregunta vs. nivel configurado.
- Pruebas `tests/test_validation.py` (26). Total acumulado: **31 verdes**.

---

## Turno 4 — "sigamos"

**Se hizo (módulo `questions_engine`):**
- `prompts.py` (prompt versionado §6a, anti-repetición), `engine.py` (orquesta: prompt → IA → validación → `GeneratedQuestion`).
- Inyección de dependencias para pruebas con stub.
- Pruebas `tests/test_questions_engine.py` (5). Total: **36 verdes**.

---

## Turno 5 — "sigue"

**Se hizo (módulo `evaluation_engine`):**
- `prompts.py` (prompt §6b), `engine.py`.
- Valida la respuesta ANTES de llamar a la IA (ahorro de costo, RNF-04).
- Evaluación multidimensional; rangos blindados (puntaje 0–100).
- Pruebas `tests/test_evaluation_engine.py` (6). Total: **42 verdes**.

---

## Turno 6 — "si"

**Se hizo (módulo `feedback`):**
- `prompts.py` (prompt §6c), `engine.py`.
- Resultado general + plan de mejora; cálculo de **promedio local** como ancla objetiva junto al puntaje de la IA.
- No resume sesión vacía (RNF-04).
- Pruebas `tests/test_feedback.py` (5). Total: **47 verdes**.

---

## Turno 7 — "si"

**Se hizo (módulo `storage`):**
- `schema.py` (6 tablas + índices), `db.py` (conexión con FK y commit/rollback), `repository.py` (CRUD + trazabilidad).
- Trazabilidad completa en `ia_trazas` (RF-10/RNF-05).
- Pruebas `tests/test_storage.py` (6) con BD SQLite temporal. Total: **52 verdes**.
- Se verificó que `entrevistas.db` queda gitignored.

---

## Turno 8 — "sigamos"

**Se hizo (módulo `interview` — orquestación):**
- `service.py`: flujo completo (iniciar → generar → responder/evaluar → finalizar).
- La BD como única fuente de verdad; inyección de dependencias total.
- Una prueba detectó que convenía validar la sesión vacía también en la orquestación → se añadió esa guarda (defensa en profundidad).
- Pruebas de integración `tests/test_interview.py` (7). Total: **58 verdes**.

---

## Turno 9 — "sigamos"

**Se hizo (módulo `api` — cierre del backend):**
- `schemas.py` (contratos Pydantic + disclaimer ético), `app.py` (FastAPI, rutas, mapeo de errores a HTTP), `app/main.py` (entrypoint).
- Endpoints REST completos; errores mapeados (400/422/404/502/503).
- Pruebas `tests/test_api.py` (10) con `TestClient` y servicio simulado. Total: **67 verdes**.
- Se verificó que la app arranca y expone todas las rutas.

**Estado:** 8/8 módulos completos, 67 pruebas verdes.

---

## Turno 10 — "genera los documentos. ¿puedo regresar a este chat?"

**Usuario:** pidió generar la documentación y preguntó si podía volver al chat para probar la API real.

**Se respondió:** sí, el chat persiste y el código está en disco; basta con poner la API key en `.env` y pedir correr los escenarios.

**Se hizo (documentación §9):**
- `README.md` (raíz).
- `docs/documentacion_tecnica.md` (arquitectura con diagrama, módulos, integración IA, datos, errores, decisiones).
- `docs/documentacion_funcional.md` (problema, usuarios, RF, flujo, entradas/salidas).
- `docs/manual_usuario.md` (guía paso a paso con `curl`).
- `docs/catalogo_prompts.md` (los 3 prompts + system base: objetivo, versión, controles, evolución).
- `docs/guia_ejecucion.md` (instalación, `.env`, arranque, pruebas, problemas comunes).
- `docs/evidencia_individual.md` (plantilla por integrante + reparto + preguntas de defensa).
- Se verificó: 6 documentos + README, 67 pruebas verdes.

---

## Turno 11 — "crea un archivo externo con la explicación + un log del chat"

**Usuario:** pidió (1) un archivo fuera del proyecto con la explicación paso a paso de cada módulo, y (2) un log de este chat dentro del proyecto.

**Se hizo:**
- `../EXPLICACION_MODULOS_PASO_A_PASO.md` (fuera del proyecto, en `ProyectoFin/`) — explicación detallada módulo por módulo.
- `BITACORA_CHAT.md` (este archivo, dentro del proyecto) — log cronológico del chat.

---

## Pendientes (para retomar)

1. **Correr los 3 escenarios reales (§7)** — junior, intermedio, arquitectura. Requiere `ANTHROPIC_API_KEY` en `.env`. Pedir a Claude: *"corre los escenarios reales"*.
2. **Llenar nombres** en `docs/evidencia_individual.md`.
3. (Opcional) **Commit inicial** del trabajo en una rama.

---

## Datos útiles

- **Arrancar servidor:** `python -m app.main` o `uvicorn app.api.app:app --reload`
- **Swagger:** http://127.0.0.1:8000/docs
- **Pruebas:** `pytest -q` (sin API key)
- **Modelo por defecto:** `claude-haiku-4-5` (configurable en `.env`)
- **Total de pruebas:** 67 (todas verdes)
