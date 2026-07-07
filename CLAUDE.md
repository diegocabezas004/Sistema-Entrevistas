# Simulador Generativo de Entrevistas Técnicas — CLAUDE.md

> Este archivo se lee automáticamente al iniciar Claude Code en esta carpeta. Es la fuente de verdad para arquitectura, requisitos, prompts de IA, documentación y criterios de calidad. Cubre el 100% de lo exigido por el enunciado del proyecto y por la rúbrica de evaluación (defensa grupal 70% + defensa individual 30%). Si algo no está claro, preguntar antes de asumir.

## 1. Resumen del proyecto

Aplicación funcional que simula entrevistas técnicas usando IA generativa como componente central del flujo (no decorativo). El sistema selecciona rol/nivel/tecnología, genera preguntas con IA, evalúa respuestas del usuario con IA, entrega retroalimentación estructurada, calcula un resultado general y propone un plan de mejora personalizado. Todo queda persistido con trazabilidad completa de prompts y respuestas de IA.

**No es válido**: listado de preguntas fijas, calculadora de nota por reglas simples sin IA, o una IA usada solo de forma decorativa.

**Condición obligatoria (rúbrica):** la IA generativa debe ser parte central del flujo funcional, no un agregado.

## 2. Stack tecnológico

- **Backend**: Python + FastAPI
- **Persistencia**: PostgreSQL (o SQLite para correr localmente en la defensa)
- **IA generativa**: Anthropic API (Claude). Modelo por defecto `claude-haiku-4-5` (más económico, suficiente para este alcance), configurable por variable de entorno para poder cambiarlo sin tocar código.
- **Frontend**: React simple (o server-rendered con Jinja2 si el grupo prefiere reducir superficie de trabajo)
- **Control de versiones**: Git/GitHub
- **Configuración**: variables de entorno vía `.env` (nunca credenciales en el código fuente — RNF-02)

## 3. Arquitectura obligatoria

Separar por responsabilidades, cada una en su propio módulo. Esto mapea directamente al criterio de rúbrica "Arquitectura, diseño técnico y calidad del código" (12% de la nota grupal):

```
/app
  /interview          -> orquestación de sesión de entrevista (configuración, estado)
  /questions_engine    -> genera preguntas llamando a la IA
  /evaluation_engine     -> evalúa respuestas llamando a la IA
  /feedback                -> arma retroalimentación + plan de mejora
  /ai_client                  -> única capa que habla con la API de Anthropic (aislada)
  /storage                       -> persistencia: entrevistas, historial, trazabilidad de prompts
  /validation                       -> validación de configuración, respuestas, coherencia, formato de salida de IA
  /api                                -> endpoints REST
/tests
/docs
  catalogo_prompts.md
  documentacion_tecnica.md
  documentacion_funcional.md
  manual_usuario.md
  guia_ejecucion.md
  evidencia_individual.md
.env.example
README.md
```

Regla dura: ningún módulo fuera de `ai_client` debe llamar directamente a la API de Anthropic. Esto permite cambiar de modelo/proveedor sin tocar el resto y centraliza el manejo de errores/reintentos.

## 4. Requisitos funcionales (RF) — implementar todos con criterio de aceptación

| Código | Requisito | Criterio de aceptación |
|---|---|---|
| RF-01 | Configuración de entrevista | Usuario define rol, tecnología, nivel, idioma, cantidad de preguntas y tipo (técnica, conceptual, práctica, situacional, arquitectura básica, mixta) antes de iniciar. |
| RF-02 | Generación de preguntas | La IA genera preguntas nuevas y contextualizadas; dos entrevistas con la misma configuración no producen el mismo set. |
| RF-03 | Registro de respuestas | El usuario responde cada pregunta y queda asociada a la entrevista en curso. |
| RF-04 | Evaluación generativa | La IA evalúa cada respuesta: precisión técnica, claridad, profundidad, estructura, riesgo de conceptos incorrectos. |
| RF-05 | Retroalimentación individual | Por pregunta: fortalezas, errores, omisiones, sugerencia de respuesta mejorada. |
| RF-06 | Resultado general | Puntaje agregado, nivel estimado, áreas fuertes, áreas de mejora al final de la entrevista. |
| RF-07 | Plan de mejora | La IA genera ruta breve de estudio/práctica basada en el desempeño real de esa entrevista. |
| RF-08 | Historial | Toda entrevista completada queda guardada y es consultable. |
| RF-09 | Comparación de avances | El usuario ve entrevistas anteriores y detecta avances o debilidades recurrentes. |
| RF-10 | Trazabilidad de IA | Se guarda prompt exacto, respuesta cruda, criterios usados y fecha/hora de cada llamada. |
| RF-11 | Validación de coherencia | El sistema detecta si una pregunta/evaluación no corresponde al rol/nivel/tecnología configurados. |
| RF-12 | Manejo de errores | Fallos de IA, respuestas incompletas, datos faltantes o formato inválido no rompen el flujo. |

## 5. Requisitos no funcionales (RNF) — cumplir todos

| Código | Categoría | Criterio de aceptación |
|---|---|---|
| RNF-01 | Arquitectura | Código organizado en los módulos de la sección 3, sin mezclar responsabilidades. |
| RNF-02 | Seguridad | API keys solo por variable de entorno; `.env` en `.gitignore`; nunca hardcodeadas. |
| RNF-03 | Privacidad | No pedir/guardar datos personales sensibles; perfiles pueden ser ficticios/académicos. |
| RNF-04 | Validación | Validar configuración vacía, respuestas vacías, estructura de evaluación, rangos de puntaje y coherencia antes de persistir o mostrar. |
| RNF-05 | Trazabilidad | Registrar prompt, respuesta de IA, criterios, fecha y versión de la entrevista. |
| RNF-06 | Manejo de errores | Mensajes claros y específicos ante datos faltantes, fallo de IA o evaluación no generable. |
| RNF-07 | Usabilidad | Flujo iniciar → responder → evaluar → revisar navegable sin ambigüedad. |
| RNF-08 | Mantenibilidad | Proyecto instalable y ejecutable siguiendo un README con pasos claros. |

## 6. Prompts de IA (obligatorio versionar y documentar — criterio "Calidad del prompting", 8%)

Diseñar como mínimo tres prompts especializados, cada uno forzando salida en **JSON estructurado**:

**a) Generación de pregunta** — entrada: rol, tecnología, nivel, tipo de entrevista, preguntas ya hechas en la sesión (evitar repetición).
```json
{
  "pregunta": "...",
  "dificultad": "junior|intermedio|senior",
  "criterios_evaluados": ["..."],
  "tema": "..."
}
```

**b) Evaluación de respuesta** — entrada: pregunta, respuesta del usuario, criterios de evaluación, nivel configurado.
```json
{
  "puntaje": 0,
  "fortalezas": ["..."],
  "errores": ["..."],
  "omisiones": ["..."],
  "respuesta_mejorada": "...",
  "coherente_con_configuracion": true
}
```

**c) Plan de mejora / resumen final** — entrada: todas las evaluaciones de la sesión.
```json
{
  "nivel_estimado": "...",
  "puntaje_general": 0,
  "areas_fuertes": ["..."],
  "areas_mejora": ["..."],
  "plan_de_estudio": ["..."]
}
```

Restricciones obligatorias en el system prompt de todos los casos:
- Nunca afirmar que el usuario aprobará una entrevista real o será contratado.
- Dejar explícito (en el prompt y en la interfaz) que la evaluación es una herramienta de práctica, no una certificación oficial.

`ai_client` debe validar que el JSON devuelto tenga los campos esperados antes de pasarlo a otras capas (RF-11, RF-12, RNF-04). Si falla la validación: reintentar una vez; si vuelve a fallar, devolver un error controlado (RNF-06).

## 7. Escenarios de prueba obligatorios (deben quedar como evidencia demostrable)

1. Entrevista **junior** — nivel bajo, preguntas conceptuales/básicas.
2. Entrevista **intermedia** — mezcla de conceptual y práctica.
3. Entrevista de **arquitectura / resolución de problemas** — mayor profundidad, preguntas de diseño.

Cada escenario debe generar una entrevista completa (preguntas → respuestas → evaluación → resultado → plan de mejora) guardada como evidencia en `/docs`.

## 8. Fuera de alcance (no implementar)

- Audio, video o reconocimiento de voz.
- Integración real con plataformas de reclutamiento.
- Entrenamiento de modelos propios.
- Despliegue en la nube (opcional, no obligatorio).
- Autenticación completa (aceptable un flujo local/académico simple).

## 9. Documentación obligatoria a generar (entregables de la rúbrica)

Además del código, generar en `/docs`:

| Archivo | Contenido mínimo |
|---|---|
| `documentacion_tecnica.md` | Arquitectura, componentes, servicios, integración con IA, configuración, dependencias, decisiones técnicas. |
| `documentacion_funcional.md` | Descripción del problema, usuarios, funcionalidades, pasos de uso, entradas, salidas, restricciones. |
| `manual_usuario.md` | Instrucciones para configurar una entrevista, responder preguntas, revisar resultados e interpretar recomendaciones. |
| `catalogo_prompts.md` | Cada prompt usado, objetivo, versión, entrada esperada, salida esperada, controles aplicados y cómo evolucionó. |
| `guia_ejecucion.md` | Pasos para instalar, configurar variables de entorno y ejecutar el sistema. |
| `evidencia_individual.md` | Por cada integrante: funcionalidades, pantallas, código, pruebas, documentación o investigación de la que fue responsable (para la defensa individual). |

`README.md` en la raíz debe resumir instalación + ejecución (cubre RNF-08 y facilita la demo).

## 10. Mapeo a criterios de la rúbrica (para que el desarrollo apunte directo a la nota)

**Defensa grupal (70%):**
- Solución efectiva del sistema (10%) → problema claro + demo coherente (secciones 1, 7).
- Arquitectura y calidad del código (12%) → sección 3.
- Uso central y correcto de IA (14%) → IA genera/evalúa/recomienda de verdad, nunca decorativa (secciones 1, 6).
- Calidad del prompting (8%) → sección 6 + `catalogo_prompts.md`.
- Integración técnica con IA (8%) → `ai_client` + manejo de errores (secciones 3, 6, RF-12).
- Datos, contexto y trazabilidad (6%) → RF-10, RNF-05.
- Seguridad, privacidad y uso responsable (6%) → RNF-02, RNF-03.
- Calidad funcional y UX (6%) → RNF-07, demo fluida sin errores críticos.
- Documentación y lineamientos (5%) → sección 9.
- Presentación grupal y profesionalismo (5%) → preparar demo controlada de los 3 escenarios de la sección 7.

**Defensa individual (30%):** cada integrante debe poder explicar su parte asignada, responder preguntas técnicas sobre el flujo de IA, y mostrar evidencia real de participación (`evidencia_individual.md`, commits por rama/módulo).

## 11. Instrucciones de trabajo para Claude Code

- Implementar por módulos, uno a la vez, en este orden: `ai_client` → `validation` → `questions_engine` → `evaluation_engine` → `feedback` → `storage` → `interview` (orquestación) → `api`.
- Después de cada módulo, dar un resumen breve de qué se implementó y por qué — necesario para que el estudiante responsable pueda explicarlo en la defensa individual. No avanzar al siguiente módulo sin ese resumen.
- Escribir pruebas básicas por módulo, especialmente `validation` y `evaluation_engine` (impactan RF-11/RF-12).
- Integrar la API real de Anthropic desde el inicio, no usar mocks permanentes.
- Generar `README.md`, `.env.example` (sin valores reales) y todos los archivos de `/docs` listados en la sección 9.
- Al completar cada escenario de prueba (sección 7), guardar la evidencia en `/docs` con preguntas, respuestas y evaluación completas.

## 12. Restricciones duras (no negociables)

- Nunca exponer API keys en el repositorio.
- La IA debe ser central al flujo — no reemplazar IA por reglas simples solo para "usarla" de forma decorativa.
- El sistema debe mostrar siempre que la evaluación es una herramienta de práctica, no un resultado oficial.
- No afirmar contratación garantizada ni aprobación de entrevista real en ningún texto generado por la IA.
