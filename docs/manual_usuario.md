# Manual de Usuario

Esta guía explica cómo usar el Simulador Generativo de Entrevistas Técnicas. Hay dos formas de usarlo:

- **Interfaz web** (recomendada): tres pantallas encadenadas en `http://127.0.0.1:8000/`. Es la que se usa en la demostración.
- **API REST**: los mismos pasos vía `curl`, Postman o la interfaz **Swagger** en `http://127.0.0.1:8000/docs`. Ver la sección 7.

> ⚠️ Recuerda: la evaluación es una **herramienta de práctica**, no una certificación oficial ni una garantía de resultado en entrevistas reales. Este aviso aparece siempre al pie del panel izquierdo de la aplicación.

---

## 1. Antes de empezar

Asegúrate de que el servidor esté corriendo (ver `guia_ejecucion.md`):

```bash
python -m app.main
```

Abre en el navegador:

```
http://127.0.0.1:8000/
```

Verás la pantalla de configuración. La aplicación se organiza siempre igual: un **panel izquierdo** con el contexto de la sesión y el recorrido de preguntas, y el **área principal** con lo que te toca hacer en ese momento.

---

## 2. Pantalla 1 — Configurar entrevista

Ruta: `/ui`

Aquí armas la entrevista que quieres practicar.

### Escenarios listos

Tres botones cargan una configuración de ejemplo en el formulario. Sirven para empezar rápido y son los tres escenarios de prueba del proyecto:

| Escenario | Configuración que carga |
|---|---|
| **Entrevista junior** | Desarrollador Backend · Python · junior · conceptual · 3 preguntas |
| **Entrevista intermedia** | Desarrollador Full Stack · JavaScript y Node.js · intermedio · mixta · 4 preguntas |
| **Arquitectura y diseño** | Ingeniero de Software Senior · Microservicios y PostgreSQL · senior · arquitectura · 3 preguntas |

Al pulsar uno, el formulario se rellena solo. Puedes ajustar cualquier campo antes de iniciar.

### Configuración

| Campo | Qué es | Valores |
|---|---|---|
| **Puesto** | El cargo al que te postularías. | Texto libre, hasta 120 caracteres. |
| **Tecnología** | Lenguaje, framework o área de las preguntas. | Texto libre, hasta 120 caracteres. |
| **Nivel** | Qué tan exigentes serán las preguntas. | Junior, Intermedio, Senior. |
| **Tipo de entrevista** | El enfoque de las preguntas. | Técnica, Conceptual, Práctica, Situacional, Arquitectura, Mixta. |
| **Preguntas** | Cuántas responderás. | De 1 a 20. |
| **Idioma** | En qué idioma pregunta y evalúa la IA. | Español, Inglés. |

Pulsa **Iniciar entrevista**. El botón cambia a *"Generando la primera pregunta…"* mientras la IA trabaja: tarda unos segundos, es normal.

### Sesiones anteriores

Debajo del formulario está el historial. Cada fila muestra puesto, tecnología, nivel, tipo, fecha y el puntaje obtenido:

- Una sesión **completada** te lleva a su pantalla de resultado.
- Una sesión **en curso** te devuelve a la pregunta donde la dejaste.

---

## 3. Pantalla 2 — Responder preguntas

Ruta: `/ui/entrevistas/{id}`

### Panel izquierdo

- **Sesión**: puesto, tecnología, nivel y tipo que configuraste. Está siempre a la vista para que respondas en el contexto correcto.
- **Preguntas**: el recorrido numerado de la entrevista. La pregunta actual aparece resaltada en ámbar, las ya evaluadas muestran su puntaje, y las que faltan aparecen como *"Por generar"*.
- **Terminar y ver resultado**: aparece en cuanto tengas al menos una respuesta evaluada, por si quieres cerrar la entrevista antes de agotar todas las preguntas.

### Área principal

1. El **número grande** indica en qué punto de la secuencia estás, junto al texto *"Pregunta N de M"* y el tema y nivel de la pregunta.
2. **Se evalúa**: las etiquetas bajo la pregunta son los criterios exactos con los que la IA calificará tu respuesta. Úsalas como guía de qué cubrir.
3. **Tu respuesta**: escribe con tus propias palabras, como lo dirías en voz alta. Máximo 5000 caracteres. No se puede enviar vacía.
4. Pulsa **Enviar respuesta**. El botón cambia a *"Evaluando tu respuesta…"*.

### Retroalimentación

Al enviar, la página vuelve con la siguiente pregunta arriba y, debajo, la evaluación de la que acabas de responder:

- **Puntaje de 0 a 100** con su banda de desempeño y una barra de referencia.
- **Lo que hiciste bien** — los aciertos que la IA reconoció.
- **Errores** — afirmaciones incorrectas o imprecisas.
- **Lo que faltó** — omisiones: temas que la respuesta debió cubrir y no cubrió.
- **Ver una respuesta más completa** — despliega una versión mejorada de tu respuesta. Es lo más útil para aprender: compárala con lo que escribiste.

Si la IA detecta que su propia evaluación no encaja con la configuración de la entrevista, aparece un aviso pidiéndote tomarla con reservas.

---

## 4. Pantalla 3 — Resultado

Ruta: `/ui/entrevistas/{id}/resultado`

Llegas aquí al responder la última pregunta, o pulsando *"Terminar y ver resultado"*.

### Cómo interpretar el resultado

| Elemento | Qué significa |
|---|---|
| **Puntaje grande (0–100)** | Estimación global de la IA sobre tu desempeño en esta sesión. |
| **Banda** | Lectura rápida del puntaje: Sólido (80+), Aceptable (60–79), En desarrollo (40–59), Inicial (menos de 40). |
| **Nivel estimado** | El nivel que refleja tu desempeño, que puede no coincidir con el que configuraste. Si pediste senior y estimó intermedio, ahí tienes la brecha a cerrar. |
| **Promedio de tus respuestas** | Promedio aritmético real de los puntajes por pregunta. Sirve de contraste objetivo frente al puntaje global. |

### Áreas fuertes y áreas de mejora

Dos columnas con lo que sostuviste bien y lo que quedó débil, agregado a partir de todas tus respuestas, no de una sola.

### Plan de estudio

Lista numerada de pasos concretos, **ordenada por lo que más te conviene atacar primero** según cómo respondiste hoy. Se genera para esta sesión: no es un temario genérico.

### Pregunta por pregunta

El desglose completo. Cada tarjeta muestra el tema, la pregunta, tu puntaje y su barra. Al desplegar **Ver tu respuesta y la retroalimentación** aparece lo que escribiste, las fortalezas, errores y omisiones, y la respuesta sugerida.

Al pie tienes **Practicar otra entrevista** y **Ver trazabilidad de la IA** (sección 8).

---

## 5. Comparar tus avances

Vuelve a `/ui` y revisa **Sesiones anteriores**. Para medir progreso de verdad:

- Repite la **misma configuración** varias veces. Las preguntas nunca se repiten, así que el puntaje sí es comparable.
- Fíjate en las **áreas de mejora que se repiten** entre sesiones: esas son tus debilidades reales, no un mal día.
- Compara el **nivel estimado** con el nivel que configuraste, no solo el puntaje.

---

## 6. Qué hacer si algo falla

Los errores aparecen como una banda roja en la parte superior del área principal, con el mensaje de qué pasó.

| Mensaje | Qué significa | Qué hacer |
|---|---|---|
| *La IA no devolvió una respuesta utilizable…* | La IA falló o devolvió algo con formato inválido. | **Recarga la página.** El sistema reintenta sin perder tu avance. |
| *El servicio de IA no está configurado…* | Falta la API key. | Configura `ANTHROPIC_API_KEY` en el archivo `.env` y reinicia el servidor. |
| *Esa entrevista no existe.* | El identificador de la URL no corresponde a ninguna sesión. | Vuelve a `/ui` y entra desde el historial. |
| Mensajes sobre un campo concreto | Un dato de la configuración o la respuesta no es válido. | Corrige el campo que indica el mensaje y reenvía. |

Como el sistema genera la pregunta y el resultado **al entrar a la pantalla**, recargar es siempre seguro: no duplica preguntas ni pierde respuestas ya guardadas.

---

## 7. Uso alternativo por API REST

Los mismos pasos sin navegador. Útil para revisar el sistema o automatizar pruebas.

| Paso | Comando |
|---|---|
| Verificar que responde | `curl http://127.0.0.1:8000/health` |
| Iniciar entrevista | `POST /entrevistas` |
| Generar pregunta | `POST /entrevistas/{id}/preguntas` |
| Responder y evaluar | `POST /entrevistas/{id}/preguntas/{pid}/respuesta` |
| Finalizar | `POST /entrevistas/{id}/finalizar` |
| Historial | `GET /entrevistas` |
| Detalle completo | `GET /entrevistas/{id}` |

Iniciar una entrevista (guarda el `entrevista_id` que devuelve):

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

Generar una pregunta (guarda el `pregunta_id`):

```bash
curl -X POST http://127.0.0.1:8000/entrevistas/1/preguntas
```

Responder y recibir la evaluación:

```bash
curl -X POST http://127.0.0.1:8000/entrevistas/1/preguntas/10/respuesta \
  -H "Content-Type: application/json" \
  -d '{ "respuesta": "Una variable es un espacio de memoria con nombre que guarda un valor." }'
```

Finalizar y obtener resultado general y plan de mejora:

```bash
curl -X POST http://127.0.0.1:8000/entrevistas/1/finalizar
```

Los campos `nivel`, `idioma` y `tipo` aceptan los mismos valores de la tabla de la sección 2, en su forma sin tildes (`tecnica`, `practica`, `arquitectura`) y con variantes comunes (`jr`, `avanzado`, `español`).

**Códigos de error de la API:**

| Código | Significado | Qué hacer |
|---|---|---|
| 400 | Dato inválido de negocio (nivel no válido, respuesta vacía). | Revisa el campo indicado en el mensaje. |
| 422 | Falta un campo o el tipo es incorrecto. | Revisa el cuerpo de la petición. |
| 404 | Entrevista no encontrada. | Verifica el `entrevista_id`. |
| 502 | La IA no pudo generar una respuesta válida. | Reintenta; si persiste, revisa la conectividad. |
| 503 | Falta configurar la API key. | Configura `ANTHROPIC_API_KEY` en `.env`. |

---

## 8. Consultar la trazabilidad de IA

Para ver exactamente qué prompts se enviaron y qué respondió la IA en cada paso (auditoría y demostración):

```bash
curl http://127.0.0.1:8000/entrevistas/1/trazas
```

También se llega desde el enlace **Ver trazabilidad de la IA** al pie de la pantalla de resultado. Cada registro incluye el prompt de sistema, el prompt de usuario, la respuesta cruda del modelo, los criterios usados, el modelo, la versión del prompt y la fecha y hora.

---

## 9. Consejos para practicar

- Responde con tus propias palabras; la IA evalúa profundidad y claridad, no memorización.
- Lee las etiquetas de **Se evalúa** antes de escribir: te dicen qué está buscando la evaluación.
- Revisa siempre la **respuesta más completa**: es donde está el aprendizaje real de cada pregunta.
- Prueba distintos niveles y tipos para variar la dificultad.
- Repite entrevistas con la misma configuración: las preguntas no se repiten y podrás medir avances.
