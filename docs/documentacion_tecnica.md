# Documentación Técnica

## 1. Visión general

El **Simulador Generativo de Entrevistas Técnicas** es una aplicación backend en Python + FastAPI que usa la API de Anthropic (Claude) como componente central para generar preguntas, evaluar respuestas y producir un plan de mejora. La persistencia es local en SQLite, con trazabilidad completa de cada interacción con la IA.

## 2. Arquitectura

El sistema separa responsabilidades en módulos independientes. La regla arquitectónica dura es: **solo `ai_client` habla con la API de Anthropic**; el resto del sistema depende de esa capa.

```
        ┌──────────────────────────── api (FastAPI) ────────────────────────────┐
        │  Recibe HTTP, mapea errores a códigos, delega en la orquestación       │
        └───────────────────────────────┬────────────────────────────────────────┘
                                         │
                        ┌────────────────▼─────────────────┐
                        │   interview (orquestación)        │
                        │   iniciar → preguntar → evaluar   │
                        │   → finalizar                     │
                        └───┬───────────┬───────────┬───────┘
                            │           │           │
              ┌─────────────▼──┐ ┌──────▼───────┐ ┌─▼──────────────┐
              │ questions_     │ │ evaluation_  │ │ feedback       │
              │ engine (RF-02) │ │ engine (RF-4)│ │ (RF-06/07)     │
              └───────┬────────┘ └──────┬───────┘ └───────┬────────┘
                      │                 │                 │
                      └────────┬────────┴────────┬────────┘
                               │                 │
                      ┌────────▼────────┐ ┌──────▼──────────┐
                      │ validation      │ │ ai_client       │
                      │ (RF-11/RNF-04)  │ │ (única capa IA) │
                      └─────────────────┘ └──────┬──────────┘
                                                 │
                                       ┌─────────▼─────────┐
                                       │  Anthropic API    │
                                       │  (Claude)         │
                                       └───────────────────┘

  storage (SQLite) ──► persiste entrevistas, preguntas, respuestas,
                       evaluaciones, resúmenes y trazas de IA (RF-10/RNF-05)
```

## 3. Componentes (módulos)

| Módulo | Responsabilidad | Requisitos cubiertos |
|---|---|---|
| `ai_client` | Única capa que llama a la API de Anthropic. Fuerza JSON, valida campos, reintenta, traza. | RF-10, RF-12, RNF-02, RNF-05 |
| `validation` | Valida configuración, respuestas, rangos, estructura y coherencia de salidas de IA. | RF-11, RF-12, RNF-04 |
| `questions_engine` | Genera preguntas contextualizadas evitando repetición. | RF-02 |
| `evaluation_engine` | Evalúa respuestas (precisión, claridad, profundidad, estructura). | RF-04, RF-05 |
| `feedback` | Resultado general + plan de mejora personalizado. | RF-06, RF-07 |
| `storage` | Persistencia SQLite y trazabilidad. | RF-08, RF-09, RF-10, RNF-05 |
| `interview` | Orquestación del ciclo de vida de la entrevista. | RF-01…RF-08 |
| `api` | Endpoints REST y manejo de errores HTTP. | RF-12, RNF-06, RNF-07 |
| `config` | Configuración central por variables de entorno. | RNF-02 |

## 4. Integración con IA

### 4.1 Capa `ai_client`

- **Aislamiento:** ningún otro módulo importa el SDK `anthropic`. Cambiar de modelo o proveedor se hace solo aquí.
- **Método principal:** `generate_json(user_prompt, required_fields, system_prompt, criterios)`.
- **System prompt base:** todas las llamadas anteponen `BASE_SYSTEM_PROMPT`, que impone las restricciones éticas (no prometer contratación, dejar claro que es práctica) y la obligación de responder solo con JSON.
- **Validación de salida:** parsea el JSON, limpia posibles fences Markdown, y verifica que existan los campos requeridos.
- **Reintentos:** si el JSON es inválido o faltan campos, reintenta (configurable, por defecto 1 vez). Si vuelve a fallar, lanza `AIResponseError` con la respuesta cruda.
- **Trazabilidad:** devuelve un `AICallResult` con prompt exacto, respuesta cruda, modelo, criterios y timestamp.

### 4.2 Modelo

- Por defecto `claude-haiku-4-5` (económico y suficiente para el alcance).
- Configurable con la variable `ANTHROPIC_MODEL` sin tocar código.

## 5. Configuración

Todas las variables se leen del entorno (archivo `.env`, cargado por `python-dotenv`):

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `ANTHROPIC_API_KEY` | Clave de la API de Anthropic (obligatoria para llamadas reales). | — |
| `ANTHROPIC_MODEL` | Modelo a usar. | `claude-haiku-4-5` |
| `ANTHROPIC_MAX_TOKENS` | Límite de tokens de salida por llamada. | `1500` |
| `AI_MAX_RETRIES` | Reintentos ante JSON inválido. | `1` |
| `DATABASE_URL` | Ruta de la base SQLite. | `sqlite:///./entrevistas.db` |
| `APP_HOST` / `APP_PORT` | Host y puerto del servidor. | `127.0.0.1` / `8000` |

## 6. Modelo de datos (SQLite)

| Tabla | Contenido |
|---|---|
| `entrevistas` | Configuración y estado (en_curso/completada) de cada entrevista. |
| `preguntas` | Preguntas generadas (enunciado, dificultad, tema, criterios). |
| `respuestas` | Respuestas del usuario por pregunta. |
| `evaluaciones` | Evaluación de cada respuesta (puntaje, fortalezas, errores, omisiones, respuesta mejorada, coherencia). |
| `resumenes` | Resultado general y plan de mejora de la entrevista. |
| `ia_trazas` | **Trazabilidad:** por cada llamada a IA — system prompt, user prompt, respuesta cruda, modelo, criterios, versión de prompt y fecha/hora. |

Integridad referencial con claves foráneas y `ON DELETE CASCADE`. Las listas se guardan como JSON en columnas de texto.

## 7. Manejo de errores (RF-12 / RNF-06)

| Situación | Excepción | Respuesta HTTP |
|---|---|---|
| Entrada/coherencia inválida | `ValidationError` | 400 (con campo) |
| Falta configuración de IA (API key) | `AIConfigError` | 503 |
| Fallo de IA (JSON inválido tras reintentos, red) | `AIResponseError` | 502 |
| Tipos/rangos de request | (Pydantic) | 422 |
| Recurso no encontrado | — | 404 |

Las operaciones de base de datos son transaccionales: si algo falla a mitad, se hace rollback (no quedan datos a medias).

## 8. Dependencias

- `fastapi`, `uvicorn` — servidor web y ASGI.
- `anthropic` — SDK oficial de la API de Claude.
- `python-dotenv` — carga de variables de entorno.
- `pydantic` — validación de contratos de API.
- `pytest`, `httpx` — pruebas.
- `sqlite3` — persistencia (librería estándar, sin instalación).

## 9. Decisiones técnicas relevantes

1. **Una sola capa de IA** para poder cambiar modelo/proveedor y centralizar errores, reintentos y trazabilidad.
2. **Salida JSON forzada y validada** en dos niveles: `ai_client` (campos presentes) + `validation` (tipos, rangos, coherencia).
3. **SQLite con stdlib** para una defensa 100% local sin servicios externos.
4. **Promedio local en el resumen** (`promedio_calculado`) como ancla objetiva, sin confiar solo en la agregación numérica de la IA.
5. **Inyección de dependencias** en motores y orquestación, para pruebas sin API real (67 pruebas automatizadas).
6. **Prompts versionados** y documentados en `catalogo_prompts.md`.

## 10. Pruebas

67 pruebas con pytest, organizadas por módulo. Usan motores/clientes simulados (stubs) para no llamar a la API real ni incurrir en costo, y una BD SQLite temporal para las pruebas de persistencia e integración.

```bash
pytest -q
```
