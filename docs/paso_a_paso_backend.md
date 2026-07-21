# Paso a paso — Backend

> Recorrido, en orden, de qué hace el backend cuando corre una entrevista.
> Sirve para entender el código y para explicarlo en la defensa individual.
> Cada paso apunta al archivo real donde ocurre.

El backend es Python + FastAPI. La regla de oro: **la lógica de negocio vive en
`InterviewService` (`app/interview/service.py`); todo lo demás son capas
delgadas alrededor.** La API REST y la web solo traducen HTTP ↔ servicio.

---

## Paso 0 — Arranque del servidor

**Archivos:** `app/main.py`, `app/config.py`, `app/api/app.py`

1. `python -m app.main` levanta uvicorn con host/puerto leídos de `.env`.
2. `app/config.py` carga **todas** las variables de entorno una sola vez en un
   objeto `Settings` inmutable (API key, modelo, tokens, reintentos, ruta de la
   BD). Nadie lee `os.environ` directo: todos piden a `settings`. Esto cumple
   RNF-02 (credenciales solo por entorno).
3. `app/api/app.py` → `create_app()` construye la app FastAPI, registra los
   manejadores de error, monta los estáticos y **incluye el router de la web**.
   La raíz `/` redirige a `/ui`.

> La API key **no** se exige al arrancar: podés correr las pruebas y validaciones
> sin credenciales. El `ai_client` la exige recién cuando hace una llamada real.

---

## Paso 1 — Iniciar entrevista (RF-01)

**Endpoint:** `POST /entrevistas` → **Servicio:** `iniciar_entrevista()`
**Archivos:** `app/api/app.py`, `app/interview/service.py`, `app/validation/`, `app/storage/`

1. Llega la configuración (rol, tecnología, nivel, idioma, cantidad, tipo).
2. `validar_config()` (en `app/validation/validators.py`) normaliza y valida:
   campos no vacíos, nivel/tipo/idioma dentro de los permitidos, cantidad de
   preguntas en rango. Si algo falla lanza `ValidationError` → la API responde
   **400** (RNF-04/RNF-06).
3. `repository.crear_entrevista()` inserta la fila en la tabla `entrevistas` con
   estado `en_curso` y devuelve el `entrevista_id`.
4. Se responde el id + la configuración normalizada + el aviso legal (disclaimer).

---

## Paso 2 — Generar la siguiente pregunta (RF-02)

**Endpoint:** `POST /entrevistas/{id}/preguntas` → **Servicio:** `generar_siguiente_pregunta()`
**Archivos:** `app/interview/service.py`, `app/questions_engine/`, `app/ai_client/`, `app/storage/`

1. El servicio lee el detalle de la entrevista desde la BD (fuente de verdad).
   Si no existe → `ValidationError`.
2. Reconstruye la configuración y junta las **preguntas previas** de la sesión.
3. Corta si ya se alcanzó la cantidad configurada (no genera de más).
4. `questions_engine.generar_pregunta(config, preguntas_previas)`:
   - arma el prompt (en `app/questions_engine/prompts.py`) con el contexto y la
     lista de preguntas ya hechas para **evitar repetición**;
   - llama a `ai_client.generate_json(...)` pidiendo los campos obligatorios
     (`pregunta`, `dificultad`, `criterios_evaluados`, `tema`);
   - el `ai_client` valida el JSON; si falla, reintenta una vez; si no, error
     controlado.
5. `repository.guardar_pregunta(...)` persiste la pregunta **y su traza de IA**
   (prompt, respuesta cruda, criterios, modelo, versión del prompt, fecha/hora).

---

## Paso 3 — Responder y evaluar (RF-03, RF-04, RF-05)

**Endpoint:** `POST /entrevistas/{id}/preguntas/{pid}/respuesta` → **Servicio:** `responder_pregunta()`
**Archivos:** `app/interview/service.py`, `app/evaluation_engine/`, `app/ai_client/`, `app/storage/`

1. Verifica que la entrevista y la pregunta existan y que la pregunta pertenezca
   a esa entrevista (si no → `ValidationError`).
2. `validar_respuesta()` limpia y valida el texto (no vacío) → RF-03/RNF-04.
3. `repository.guardar_respuesta()` persiste la respuesta.
4. `evaluation_engine.evaluar_respuesta(config, pregunta, respuesta, criterios)`
   llama a la IA con el prompt de evaluación y pide los campos: `puntaje`,
   `fortalezas`, `errores`, `omisiones`, `respuesta_mejorada`,
   `coherente_con_configuracion`.
5. Se valida el rango del puntaje y la coherencia con la configuración (RF-11).
6. `repository.guardar_evaluacion(...)` persiste la evaluación **y su traza**.
7. Se devuelve el resumen de la evaluación (la retroalimentación de esa pregunta).

---

## Paso 4 — Finalizar: resultado + plan de mejora (RF-06, RF-07)

**Endpoint:** `POST /entrevistas/{id}/finalizar` → **Servicio:** `finalizar_entrevista()`
**Archivos:** `app/interview/service.py`, `app/feedback/`, `app/ai_client/`, `app/storage/`

1. Reúne todas las evaluaciones de la sesión (pregunta, tema, puntaje,
   fortalezas, errores, omisiones).
2. **Defensa en profundidad:** si no hay respuestas evaluadas, no finaliza
   (`ValidationError`) — no depende solo del motor de feedback.
3. `feedback_engine.generar_resumen(config, items)` llama a la IA con el prompt de
   resumen y pide: `nivel_estimado`, `puntaje_general`, `areas_fuertes`,
   `areas_mejora`, `plan_de_estudio`. Además calcula un promedio propio como
   contraste al puntaje que da la IA.
4. `repository.guardar_resumen(...)` persiste el resumen **y su traza**, y
   `completar_entrevista()` marca la entrevista como `completada`.

---

## Paso 5 — Consultas: historial y trazabilidad (RF-08, RF-09, RF-10)

**Endpoints:** `GET /entrevistas`, `GET /entrevistas/{id}`, `GET /entrevistas/{id}/trazas`
**Archivos:** `app/interview/service.py`, `app/storage/repository.py`

- `listar_historial()` → todas las entrevistas (para ver avances entre sesiones).
- `obtener_entrevista(id)` → detalle completo (preguntas, respuestas,
  evaluaciones, resumen). Devuelve 404 si no existe.
- `obtener_trazas(id)` → todas las llamadas a IA de esa entrevista: prompt
  exacto, respuesta cruda, criterios, modelo, versión y fecha/hora (RF-10/RNF-05).

---

## La capa `ai_client` — el corazón de la integración

**Archivos:** `app/ai_client/client.py`, `app/ai_client/errors.py`

Es el **único** módulo que importa el SDK de Anthropic. Método principal:
`generate_json(user_prompt, required_fields, system_prompt, criterios)`.

1. Antepone un **system prompt base** con las restricciones duras (nunca prometer
   contratación/aprobación real; siempre aclarar que es práctica; responder solo
   JSON válido).
2. Llama a la API de Anthropic con el modelo configurado.
3. Limpia la respuesta (quita fences ```` ```json ````), extrae el objeto JSON y
   lo parsea.
4. Valida que estén **todos** los campos obligatorios.
5. Si algo falla → reintenta (según `AI_MAX_RETRIES`); si se agota → lanza
   `AIResponseError` con la respuesta cruda para trazabilidad.
6. Devuelve un `AICallResult` con el JSON validado **más** todo lo necesario para
   trazabilidad (prompt exacto, respuesta cruda, modelo, timestamp, intentos).

Por qué está aislado: permite cambiar de modelo/proveedor sin tocar el resto,
y centraliza errores, reintentos y trazabilidad en un solo lugar.

---

## Manejo de errores (RF-12 / RNF-06)

En `app/api/app.py` hay manejadores que traducen excepciones de dominio a HTTP:

| Excepción | HTTP | Significado |
|---|---|---|
| `ValidationError` | 400 | Datos de entrada inválidos |
| `AIConfigError` | 503 | Falta configuración (p. ej. API key) |
| `AIClientError` | 502 | La IA falló tras reintentos |
| inesperado | 500 | Error no previsto |

Ningún fallo de IA, dato faltante o formato inválido rompe el flujo: siempre hay
un mensaje claro y específico.

---

## Persistencia (`storage`)

**Archivos:** `app/storage/schema.py`, `db.py`, `repository.py`

- `schema.py` — DDL idempotente. Tablas: `entrevistas`, `preguntas`,
  `respuestas`, `evaluaciones`, `resumenes` y `ia_trazas`. Claves foráneas con
  `ON DELETE CASCADE`.
- `ia_trazas` es la tabla de trazabilidad: guarda cada llamada a la IA.
- `db.py` — conexión SQLite (activa `PRAGMA foreign_keys=ON`).
- `repository.py` — todas las operaciones de lectura/escritura. Es la única capa
  que ejecuta SQL.

---

## Orden recomendado para estudiarlo / defenderlo

`ai_client` → `validation` → `questions_engine` → `evaluation_engine` →
`feedback` → `storage` → `interview` (orquestación) → `api`.

Es el mismo orden en que se construyó y en que las dependencias fluyen: primero
la capa de IA y las validaciones, luego los motores que las usan, después la
persistencia, y al final la orquestación y la exposición HTTP.

---

## Cómo verificar el backend

```bash
source venv/bin/activate
pytest -q                          # las 80 pruebas (corren sin API key)
pytest tests/test_ai_client.py -v  # o un módulo puntual
```
