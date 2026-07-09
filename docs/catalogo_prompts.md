# Catálogo de Prompts

Este documento registra cada prompt usado por la IA: objetivo, versión, entrada esperada, salida esperada, controles aplicados y evolución. Todos los prompts fuerzan salida en **JSON estructurado** y comparten un **system prompt base** con las restricciones éticas obligatorias.

---

## 0. System prompt base (común a todos)

**Ubicación:** `app/ai_client/client.py` → `BASE_SYSTEM_PROMPT`

Se antepone a **todas** las llamadas a la IA. Impone:

- La evaluación es una herramienta de **práctica**, no una certificación oficial.
- **Nunca** afirmar que la persona aprobará una entrevista real o será contratada.
- Responder **siempre** con un único objeto JSON válido, sin texto adicional ni Markdown.

> Texto:
> *"Eres un asistente de práctica para entrevistas técnicas. Tu evaluación es una herramienta de estudio y práctica, NO una certificación oficial ni una garantía de resultado. NUNCA afirmes que la persona aprobará una entrevista real, será contratada, ni des garantías sobre procesos de reclutamiento reales. Respondes SIEMPRE con un único objeto JSON válido, sin texto antes ni después, sin comentarios y sin bloques de código Markdown."*

**Control transversal:** `ai_client` valida que el JSON devuelto tenga los campos esperados; si no, reintenta una vez y, si vuelve a fallar, devuelve un error controlado.

---

## 1. Prompt de generación de pregunta

- **Objetivo:** generar una pregunta de entrevista nueva y contextualizada (RF-02).
- **Versión:** 1.0
- **Ubicación:** `app/questions_engine/prompts.py`

### Entrada esperada
- Rol, tecnología, nivel, tipo de entrevista, idioma.
- Lista de preguntas ya realizadas en la sesión (para evitar repetición).

### Salida esperada (JSON)
```json
{
  "pregunta": "...",
  "dificultad": "junior|intermedio|senior",
  "criterios_evaluados": ["..."],
  "tema": "..."
}
```

### Controles aplicados
- La `dificultad` debe coincidir con el nivel configurado (se valida en `validation`, RF-11).
- Se listan explícitamente las preguntas previas con instrucción de no repetirlas.
- Instrucción de idioma (es/en) y de tipo de entrevista.
- Validación de campos obligatorios en `ai_client` + validación de estructura/coherencia en `validation`.

### Evolución
- **1.0** — versión inicial: JSON estricto con los cuatro campos, anti-repetición por lista de previas y coincidencia de dificultad con el nivel.

---

## 2. Prompt de evaluación de respuesta

- **Objetivo:** evaluar la respuesta del usuario de forma estructurada (RF-04/RF-05).
- **Versión:** 1.0
- **Ubicación:** `app/evaluation_engine/prompts.py`

### Entrada esperada
- Rol, tecnología, nivel configurado.
- Pregunta y respuesta del usuario.
- Criterios de evaluación asociados a la pregunta.

### Salida esperada (JSON)
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

### Controles aplicados
- El `puntaje` es un entero de 0 a 100 (rango validado en `validation`, RF-12).
- Evaluación multidimensional: precisión técnica, claridad, profundidad, estructura, riesgo de conceptos incorrectos.
- La exigencia se ajusta al nivel (junior más permisivo que senior).
- `coherente_con_configuracion` es booleano estricto (RF-11).
- Prohibición de prometer contratación/aprobación (heredada del system base).

### Evolución
- **1.0** — versión inicial: rúbrica multidimensional, escala 0–100 y bandera de coherencia.

---

## 3. Prompt de resumen final y plan de mejora

- **Objetivo:** sintetizar el desempeño global y proponer un plan de mejora personalizado (RF-06/RF-07).
- **Versión:** 1.0
- **Ubicación:** `app/feedback/prompts.py`

### Entrada esperada
- Configuración de la entrevista.
- Todas las evaluaciones de la sesión (pregunta, tema, puntaje, fortalezas, errores, omisiones).

### Salida esperada (JSON)
```json
{
  "nivel_estimado": "junior|intermedio|senior",
  "puntaje_general": 0,
  "areas_fuertes": ["..."],
  "areas_mejora": ["..."],
  "plan_de_estudio": ["paso 1", "paso 2"]
}
```

### Controles aplicados
- El plan debe basarse en el desempeño **real** de la entrevista (no genérico).
- `nivel_estimado` restringido a junior/intermedio/senior (validado).
- `puntaje_general` en rango 0–100.
- Además, el sistema calcula un **promedio local** de los puntajes por pregunta como referencia objetiva, independiente de la estimación de la IA.
- Reiteración de que es práctica, no certificación.

### Evolución
- **1.0** — versión inicial: síntesis basada en evidencia de la sesión + plan accionable.

---

## Resumen de controles de calidad del prompting

| Control | Cómo se aplica |
|---|---|
| Salida JSON estructurada | Instrucción explícita + parseo/validación en `ai_client`. |
| Campos obligatorios | Lista `required_fields` verificada antes de entregar. |
| Reintento ante fallo | 1 reintento configurable; luego error controlado. |
| Coherencia con configuración | Validación cruzada dificultad↔nivel y bandera booleana. |
| Rangos válidos | Puntajes 0–100 validados. |
| Restricciones éticas | System prompt base en todas las llamadas. |
| Versionado | Constante `PROMPT_*_VERSION` por prompt, guardada en la traza. |
| Trazabilidad | Prompt exacto y respuesta cruda persistidos en `ia_trazas`. |
