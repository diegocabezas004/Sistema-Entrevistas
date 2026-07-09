# Manual de Usuario

Esta guía explica cómo usar el Simulador Generativo de Entrevistas Técnicas a través de su API REST. Puedes usar la interfaz interactiva **Swagger** en `http://127.0.0.1:8000/docs` o herramientas como `curl`/Postman.

> ⚠️ Recuerda: la evaluación es una **herramienta de práctica**, no una certificación oficial ni una garantía de resultado en entrevistas reales.

---

## 1. Antes de empezar

Asegúrate de que el servidor esté corriendo (ver `guia_ejecucion.md`):

```bash
python -m app.main
```

Verifica que responde:

```bash
curl http://127.0.0.1:8000/health
```

---

## 2. Configurar e iniciar una entrevista

Define rol, tecnología, nivel, idioma, cantidad de preguntas y tipo.

```bash
curl -X POST http://127.0.0.1:8000/entrevistas \
  -H "Content-Type: application/json" \
  -d '{
    "rol": "Backend Developer",
    "tecnologia": "Python",
    "nivel": "junior",
    "idioma": "es",
    "cantidad_preguntas": 3,
    "tipo": "conceptual"
  }'
```

Respuesta (guarda el `entrevista_id`):

```json
{ "entrevista_id": 1, "config": { ... }, "aviso": "Esta es una herramienta de práctica..." }
```

**Opciones válidas:**
- **nivel:** `junior`, `intermedio`, `senior` (acepta variantes como "JR", "avanzado").
- **idioma:** `es`, `en`.
- **cantidad_preguntas:** 1 a 20.
- **tipo:** `tecnica`, `conceptual`, `practica`, `situacional`, `arquitectura`, `mixta`.

---

## 3. Generar una pregunta

```bash
curl -X POST http://127.0.0.1:8000/entrevistas/1/preguntas
```

Respuesta (guarda el `pregunta_id`):

```json
{
  "pregunta_id": 10,
  "orden": 1,
  "total": 3,
  "pregunta": "¿Qué es una variable en Python?",
  "dificultad": "junior",
  "criterios_evaluados": ["claridad", "precisión"],
  "tema": "Fundamentos"
}
```

---

## 4. Responder y recibir evaluación

```bash
curl -X POST http://127.0.0.1:8000/entrevistas/1/preguntas/10/respuesta \
  -H "Content-Type: application/json" \
  -d '{ "respuesta": "Una variable es un espacio de memoria con nombre que guarda un valor." }'
```

Respuesta:

```json
{
  "pregunta_id": 10,
  "puntaje": 80,
  "fortalezas": ["definición clara"],
  "errores": [],
  "omisiones": ["no mencionó tipos dinámicos"],
  "respuesta_mejorada": "Una variable en Python es...",
  "coherente_con_configuracion": true
}
```

Repite los pasos 3 y 4 hasta responder todas las preguntas.

---

## 5. Finalizar la entrevista

Genera el resultado general y el plan de mejora:

```bash
curl -X POST http://127.0.0.1:8000/entrevistas/1/finalizar
```

Respuesta:

```json
{
  "entrevista_id": 1,
  "nivel_estimado": "junior",
  "puntaje_general": 78,
  "promedio_calculado": 76.7,
  "areas_fuertes": ["fundamentos"],
  "areas_mejora": ["estructuras de datos"],
  "plan_de_estudio": ["Repasar listas y diccionarios", "Practicar problemas de complejidad"],
  "aviso": "Esta es una herramienta de práctica..."
}
```

**Cómo interpretar el resultado:**
- **puntaje_general:** estimación global de la IA (0–100).
- **promedio_calculado:** promedio real de los puntajes por pregunta (referencia objetiva).
- **areas_fuertes / areas_mejora:** en qué destacaste y en qué enfocarte.
- **plan_de_estudio:** pasos concretos para mejorar, basados en esta entrevista.

---

## 6. Consultar historial y avances

Listar todas las entrevistas:

```bash
curl http://127.0.0.1:8000/entrevistas
```

Ver el detalle completo de una:

```bash
curl http://127.0.0.1:8000/entrevistas/1
```

Compara el `puntaje_general` de entrevistas anteriores para ver tu progreso (RF-09).

---

## 7. Consultar la trazabilidad de IA

Para ver exactamente qué prompts se enviaron y qué respondió la IA (auditoría/demostración):

```bash
curl http://127.0.0.1:8000/entrevistas/1/trazas
```

---

## 8. Mensajes de error frecuentes

| Código | Significado | Qué hacer |
|---|---|---|
| 400 | Dato inválido de negocio (p. ej. nivel no válido, respuesta vacía). | Revisa el campo indicado en el mensaje. |
| 422 | Falta un campo o el tipo es incorrecto. | Revisa el cuerpo de la petición. |
| 404 | Entrevista no encontrada. | Verifica el `entrevista_id`. |
| 502 | La IA no pudo generar una respuesta válida. | Reintenta; si persiste, revisa la conectividad. |
| 503 | Falta configurar la API key. | Configura `ANTHROPIC_API_KEY` en `.env`. |

---

## 9. Consejos para practicar

- Responde con tus propias palabras; la IA evalúa profundidad y claridad, no memorización.
- Prueba distintos niveles y tipos para variar la dificultad.
- Revisa la **respuesta mejorada** de cada evaluación: es una guía de cómo responder mejor.
- Repite entrevistas con la misma configuración: las preguntas no se repiten y podrás medir avances.
