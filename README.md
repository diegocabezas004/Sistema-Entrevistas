# Simulador Generativo de Entrevistas Técnicas

Aplicación que simula entrevistas técnicas usando **IA generativa (Claude / Anthropic)** como componente central del flujo: genera preguntas, evalúa respuestas, entrega retroalimentación estructurada, calcula un resultado general y propone un plan de mejora personalizado. Todo queda persistido con **trazabilidad completa** de prompts y respuestas de IA.

> ⚠️ **Aviso:** Esta es una herramienta de **práctica**, no una certificación oficial ni una garantía de resultados en procesos de reclutamiento reales.

---

## Características

- 🤖 **IA central, no decorativa** — la IA genera, evalúa y recomienda de verdad.
- 🧩 **Arquitectura modular** — cada responsabilidad en su módulo (una sola capa habla con la IA).
- 🔍 **Coherencia validada** — detecta si una pregunta/evaluación no corresponde al rol/nivel/tecnología.
- 🗃️ **Trazabilidad total** — se guarda prompt exacto, respuesta cruda, criterios, modelo y fecha/hora de cada llamada.
- 🧪 **Pruebas automatizadas** — 67 pruebas que corren sin API key (motores simulados).
- 📊 **Historial y comparación de avances** entre entrevistas.

---

## Stack

- **Backend:** Python + FastAPI
- **IA:** Anthropic API (Claude) — modelo por defecto `claude-haiku-4-5`, configurable por `.env`
- **Persistencia:** SQLite (librería estándar `sqlite3`)
- **Pruebas:** pytest

---

## Instalación rápida

```bash
# 1. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env y colocar tu ANTHROPIC_API_KEY (obtenla en https://console.anthropic.com/)
```

## Ejecución

```bash
# Arrancar el servidor
python -m app.main
# o bien:
uvicorn app.api.app:app --reload

# Documentación interactiva (Swagger):
#   http://127.0.0.1:8000/docs
```

## Pruebas

```bash
pytest -q          # corren sin API key (usan motores simulados)
```

---

## Flujo de uso (API)

| Paso | Método | Endpoint |
|---|---|---|
| Iniciar entrevista | `POST` | `/entrevistas` |
| Generar pregunta | `POST` | `/entrevistas/{id}/preguntas` |
| Responder y evaluar | `POST` | `/entrevistas/{id}/preguntas/{pid}/respuesta` |
| Finalizar (resumen + plan) | `POST` | `/entrevistas/{id}/finalizar` |
| Ver historial | `GET` | `/entrevistas` |
| Ver detalle | `GET` | `/entrevistas/{id}` |
| Ver trazabilidad de IA | `GET` | `/entrevistas/{id}/trazas` |

Ejemplo de inicio:

```bash
curl -X POST http://127.0.0.1:8000/entrevistas \
  -H "Content-Type: application/json" \
  -d '{"rol":"Backend Developer","tecnologia":"Python","nivel":"junior","idioma":"es","cantidad_preguntas":3,"tipo":"conceptual"}'
```

---

## Estructura del proyecto

```
/app
  /ai_client         -> única capa que habla con la API de Anthropic
  /validation        -> validación de config, respuestas, coherencia, salidas de IA
  /questions_engine  -> genera preguntas con IA
  /evaluation_engine -> evalúa respuestas con IA
  /feedback          -> resultado general + plan de mejora con IA
  /storage           -> persistencia SQLite + trazabilidad
  /interview         -> orquestación del flujo completo
  /api               -> endpoints REST (FastAPI)
  config.py          -> configuración central (variables de entorno)
  main.py            -> punto de entrada
/tests               -> 67 pruebas automatizadas
/docs                -> documentación técnica, funcional, manual, prompts, etc.
```

---

## Seguridad y privacidad

- La API key **solo** se lee de variables de entorno; nunca está en el código (RNF-02).
- `.env` está en `.gitignore`; nunca se sube al repositorio.
- No se piden ni guardan datos personales sensibles; los perfiles pueden ser ficticios/académicos (RNF-03).

---

## Documentación

Ver la carpeta [`/docs`](./docs):

- [`documentacion_tecnica.md`](./docs/documentacion_tecnica.md)
- [`documentacion_funcional.md`](./docs/documentacion_funcional.md)
- [`manual_usuario.md`](./docs/manual_usuario.md)
- [`catalogo_prompts.md`](./docs/catalogo_prompts.md)
- [`guia_ejecucion.md`](./docs/guia_ejecucion.md)
- [`evidencia_individual.md`](./docs/evidencia_individual.md)
