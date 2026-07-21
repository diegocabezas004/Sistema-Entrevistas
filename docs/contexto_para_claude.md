# Contexto del proyecto para pegar en el chat de Claude

> Copiá y pegá este archivo completo en un chat nuevo de Claude cuando quieras
> que entienda el proyecto sin darle acceso al código. Resume qué es, cómo está
> armado, qué hace cada pieza y en qué estado está. Está actualizado al commit
> `7b71695` (UI en Jinja2 agregada).

---

## 1. Qué es

**Simulador Generativo de Entrevistas Técnicas.** Una aplicación web que simula
entrevistas técnicas usando IA generativa (Claude / Anthropic) como el motor
central del flujo. El sistema:

1. Deja al usuario configurar una entrevista (rol, tecnología, nivel, idioma,
   cantidad de preguntas y tipo).
2. **Genera preguntas** nuevas y contextualizadas con IA (no hay banco fijo).
3. El usuario responde cada pregunta.
4. La IA **evalúa** cada respuesta (precisión, claridad, profundidad, estructura,
   conceptos incorrectos) y da retroalimentación por pregunta.
5. Al terminar, la IA produce un **resultado general** (puntaje, nivel estimado,
   áreas fuertes/débiles) y un **plan de mejora** personalizado.
6. Todo se guarda con **trazabilidad completa** de cada llamada a la IA (prompt
   exacto, respuesta cruda, criterios, modelo, versión del prompt, fecha/hora).

Es un proyecto académico (ESEN). La condición no negociable de la rúbrica: la IA
debe ser **central al flujo funcional**, no decorativa. No vale banco de preguntas
fijo ni calcular la nota con reglas simples.

## 2. Stack

- **Backend:** Python 3.13 + FastAPI.
- **IA:** Anthropic API (Claude). Modelo por defecto `claude-haiku-4-5`,
  configurable por `.env` sin tocar código.
- **Persistencia:** SQLite (vía `sqlite3` de la librería estándar).
- **Frontend:** server-rendered con Jinja2 (sin React ni JS de framework).
- **Pruebas:** pytest — 80 pruebas que corren **sin API key** (usan motores
  simulados por inyección de dependencias).

## 3. Arquitectura (por módulos, una responsabilidad cada uno)

```
/app
  /ai_client         Única capa que habla con la API de Anthropic. REGLA DURA:
                     ningún otro módulo importa el SDK de Anthropic.
  /validation        Valida configuración, respuestas, coherencia y salidas de IA.
  /questions_engine  Genera preguntas con IA (prompt + parseo).
  /evaluation_engine Evalúa respuestas con IA.
  /feedback          Resultado general + plan de mejora con IA.
  /storage           Persistencia SQLite + trazabilidad (schema, db, repository).
  /interview         Orquestación: une todo y define el flujo de la sesión.
  /api               Endpoints REST (FastAPI).
  /web               Interfaz Jinja2 (rutas, plantillas, estilos).
  config.py          Configuración central (lee variables de entorno).
  main.py            Punto de entrada del servidor.
/tests               80 pruebas.
/docs                Documentación técnica, funcional, manual, catálogo de prompts.
```

**Regla clave de diseño:** tanto la API REST (`/api`) como la web (`/web`) son
capas de presentación delgadas. Ninguna tiene lógica de negocio: las dos llaman
al mismo `InterviewService` (en `/interview`). Ese servicio es la única fuente de
orquestación, y la base de datos es la única fuente de verdad del estado (no se
guarda estado en memoria, así el flujo sobrevive reinicios).

## 4. Flujo funcional

```
iniciar → generar pregunta → responder (evaluar) → ... → finalizar (resumen + plan)
```

Cada paso: valida entrada → llama a la IA por su motor → persiste con trazabilidad.

## 5. La IA: cómo se usa (lo central de la rúbrica)

Hay **tres prompts especializados**, cada uno fuerza salida en **JSON estructurado**:

- **Generación de pregunta** — entra rol/tecnología/nivel/tipo + preguntas ya
  hechas (para no repetir). Sale: `pregunta`, `dificultad`, `criterios_evaluados`,
  `tema`.
- **Evaluación de respuesta** — entra pregunta + respuesta del usuario + criterios
  + nivel. Sale: `puntaje`, `fortalezas`, `errores`, `omisiones`,
  `respuesta_mejorada`, `coherente_con_configuracion`.
- **Plan de mejora / resumen** — entra todas las evaluaciones de la sesión. Sale:
  `nivel_estimado`, `puntaje_general`, `areas_fuertes`, `areas_mejora`,
  `plan_de_estudio`.

Todos los prompts comparten un **system prompt base** con restricciones duras:
nunca prometer que aprobará una entrevista real o será contratado; siempre dejar
claro que es una herramienta de práctica, no una certificación; y responder
siempre con un único objeto JSON válido.

El `ai_client` valida que el JSON tenga los campos esperados **antes** de pasarlo a
otras capas. Si falla: reintenta una vez; si vuelve a fallar, lanza un error
controlado (no rompe el flujo).

## 6. Cómo se corre

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # y poner ANTHROPIC_API_KEY
python -m app.main            # o: uvicorn app.api.app:app --reload
```

- Interfaz web: `http://127.0.0.1:8000/` (redirige a `/ui`).
- API docs (Swagger): `http://127.0.0.1:8000/docs`.
- Pruebas: `pytest -q` (corren sin API key).

## 7. Estado actual

- Backend completo y funcionando (los 8 módulos).
- API REST completa.
- Interfaz web en Jinja2 con tres pantallas (configurar → responder → resultado).
- 80 pruebas verdes (67 de backend + 13 de la web).
- Documentación en `/docs`.
- Evidencia de los 3 escenarios obligatorios (junior, intermedio, arquitectura).

## 8. Cómo pedirme ayuda a partir de acá

Cuando me consultes algo, ya tenés el contexto arriba. Ejemplos útiles:
"explicame cómo funciona el evaluation_engine", "ayudame a preparar la defensa
individual del módulo X", "revisá si el manejo de errores de la web cubre RF-12",
"agregá una pantalla de historial detallado", etc.
