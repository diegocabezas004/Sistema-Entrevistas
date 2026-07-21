# Escenario 1 — Entrevista Junior (conceptual/básica)

> ⚠️ Esta evaluación es una **herramienta de práctica**, no una certificación oficial ni garantía de contratación.

- **Entrevista ID:** 1
- **Rol:** Desarrollador Backend
- **Tecnología:** Python
- **Nivel configurado:** junior
- **Tipo:** conceptual  |  **Idioma:** es
- **Cantidad de preguntas:** 3
- **Modelo IA:** claude-haiku-4-5
- **Estado:** completada

## Preguntas, respuestas y evaluación

### Pregunta 1 — Estructuras de datos en Python (dificultad: junior)

**Pregunta (IA):** Explica la diferencia entre una lista y una tupla en Python. ¿Cuáles son las principales características de cada una y en qué situaciones utilizarías una sobre la otra?

**Criterios evaluados:** Comprensión de tipos de datos, Mutabilidad vs inmutabilidad, Casos de uso prácticos, Características fundamentales

**Respuesta del candidato:**

> Bueno, la principal diferencia es que las listas son mutables y las tuplas no. Eso significa que puedo modificar una lista después de crearla, agregando o eliminando elementos, pero las tuplas son inmutables, no puedo cambiarlas.

Las listas se crean con corchetes `[1, 2, 3]` y las tuplas con paréntesis `(1, 2, 3)`. Las listas son más lentas porque permiten cambios, mientras que las tuplas son más rápidas.

Usaría listas cuando necesito modificar datos, como agregar elementos a un carrito de compras. Las tuplas las uso cuando quiero datos que no cambien, como coordenadas o para usarlas como claves en diccionarios, porque las listas no se pueden usar como claves.

**Evaluación de la IA — puntaje: 78/100**

- Coherente con la configuración (RF-11): ✅ sí

- **Fortalezas:**
  - Identifica correctamente la diferencia fundamental: mutabilidad vs inmutabilidad
  - Reconoce la sintaxis correcta para ambas estructuras (corchetes y paréntesis)
  - Proporciona casos de uso prácticos y relevantes (carrito de compras, coordenadas)
  - Menciona un aspecto importante: las tuplas pueden usarse como claves de diccionarios mientras que las listas no
  - La respuesta es clara y bien estructurada para un nivel junior

- **Errores:**
  - La afirmación sobre velocidad es imprecisa: las tuplas son más rápidas principalmente por su inmutabilidad y menor consumo de memoria, no simplemente 'porque no permiten cambios'. La diferencia de velocidad es generalmente marginal en operaciones normales
  - No menciona que ambas estructuras son secuenciales y ordenadas, lo cual es una característica fundamental

- **Omisiones:**
  - No menciona métodos específicos de listas (append, remove, extend, etc.) que demuestren la mutabilidad
  - No explica que las tuplas pueden desempaquetarse más eficientemente
  - Podría haber mencionado que las tuplas son hashable gracias a su inmutabilidad, lo que explica mejor por qué funcionan como claves
  - No toca la creación de tuplas de un elemento con coma: `(1,)` es una característica peculiar
  - Podría haber mencionado casos de uso adicionales como retorno múltiple de funciones o parámetros *args

- **Respuesta mejorada sugerida:**

  > La principal diferencia es que las listas son mutables (se pueden modificar después de crearlas) y las tuplas son inmutables (no se pueden cambiar). Las listas se crean con corchetes `[1, 2, 3]` y las tuplas con paréntesis `(1, 2, 3)`. Ambas son secuencias ordenadas que mantienen el orden de sus elementos.

Características principales:
- Listas: permiten agregar (append), eliminar (remove) y modificar elementos. Pueden contener cualquier tipo de dato.
- Tuplas: una vez creadas, no se pueden modificar. Por su inmutabilidad, son hashable y pueden usarse como claves de diccionarios, mientras que las listas no.

Uso práctico:
- Listas: cuando necesito datos que cambiarán, como un carrito de compras, una lista de tareas que puedo actualizar.
- Tuplas: cuando quiero proteger datos que no deben cambiar (coordenadas, fechas), cuando necesito usar una estructura como clave de diccionario, o cuando devuelvo múltiples valores de una función.

Las tuplas también son ligeramente más eficientes en memoria, lo que las hace mejores para grandes volúmenes de datos inmutables.

### Pregunta 2 — Diccionarios y estructuras de datos en Python (dificultad: junior)

**Pregunta (IA):** Explica qué es un diccionario en Python y cómo funciona internamente. ¿Cuál es la diferencia entre las claves y los valores, y por qué las claves deben ser inmutables?

**Criterios evaluados:** Comprensión de estructuras de datos en Python, Entendimiento de mutabilidad e inmutabilidad, Conocimiento de tipos de datos hashable, Capacidad de explicar conceptos teóricos fundamentales

**Respuesta del candidato:**

> Bueno, un diccionario es una estructura de datos que almacena pares clave-valor. Básicamente funciona como un mapeo, donde cada clave apunta a un valor específico.

Internamente, Python usa tablas hash para los diccionarios, lo que permite búsquedas muy rápidas. La clave se hashea para encontrar la ubicación del valor en memoria.

Las claves y valores son diferentes porque las claves son identificadores únicos que usas para acceder a los datos, mientras que los valores son los datos actuales que quieres almacenar.

Las claves deben ser inmutables porque si cambiasen después de hashearlas, Python no podría encontrarlas después. Si usas una lista como clave, el hash cambiaría si modificas la lista. Por eso solo puedes usar strings, números o tuplas inmutables como claves.

**Evaluación de la IA — puntaje: 78/100**

- Coherente con la configuración (RF-11): ✅ sí

- **Fortalezas:**
  - Explicación clara y accesible del concepto básico de diccionarios como estructura clave-valor
  - Comprensión correcta de que Python usa tablas hash internamente para implementar diccionarios
  - Entendimiento sólido de por qué las claves deben ser inmutables, con justificación basada en el comportamiento del hash
  - Ejemplos concretos de tipos permitidos (strings, números, tuplas) e impedidos (listas)
  - Respuesta bien estructurada y sin errores técnicos significativos

- **Errores:**
  - Afirmación imprecisa: 'cada clave apunta a un valor' sugiere una relación directa que no es del todo clara; sería más preciso decir que el hash de la clave determina la ubicación
  - No menciona explícitamente el concepto de 'hashable' como propiedad que deben cumplir las claves

- **Omisiones:**
  - No explica qué ocurre en caso de colisión de hash (aunque es tema avanzado para junior)
  - No menciona que los valores SÍ pueden ser mutables (listas, diccionarios, etc.) a diferencia de las claves
  - Podría haber mencionado el método __hash__() que Python usa internamente
  - No comenta que tuplas solo son válidas como claves si sus elementos son inmutables
  - No describe la complejidad temporal O(1) promedio de búsqueda, acceso y eliminación

- **Respuesta mejorada sugerida:**

  > Un diccionario en Python es una estructura de datos que almacena pares clave-valor. Las claves son identificadores únicos e inmutables que usas para acceder a los datos, mientras que los valores son los datos reales que deseas almacenar (pueden ser mutables o no). Internamente, Python usa tablas hash: cada clave se hashea (mediante __hash__()) para determinar su ubicación en memoria, permitiendo búsquedas muy rápidas con complejidad O(1) en promedio. Las claves deben ser inmutables porque si cambiasen después de ser hasheadas, Python no podría encontrarlas: si usas una lista como clave y luego la modificas, su hash cambiaría y la búsqueda fallaría. Por eso solo puedes usar tipos hashable como claves: strings, números, tuplas inmutables. Los valores, en cambio, pueden ser cualquier tipo, incluso listas o diccionarios. Una tupla solo es válida como clave si todos sus elementos son también inmutables.

### Pregunta 3 — Generadores en Python (dificultad: junior)

**Pregunta (IA):** Explica qué es un generador en Python y cuál es la diferencia fundamental entre un generador y una función común. ¿Cuáles son las ventajas de usar generadores en términos de memoria y eficiencia?

**Criterios evaluados:** Comprensión de generadores y la palabra clave 'yield', Diferencia entre retorno de valores completos vs evaluación perezosa, Ventajas de memoria y rendimiento, Conocimiento de iteradores y el protocolo de iteración

**Respuesta del candidato:**

> Un generador es como una función, pero en lugar de devolver todo de una vez con `return`, usa `yield` para devolver valores uno a uno. Cuando llamas un generador, no ejecuta el código inmediatamente, sino que crea un objeto que puedes iterar.

La diferencia principal es que una función común calcula todos los resultados y los guarda en memoria, mientras que un generador los produce bajo demanda, lo que ahorra mucha memoria.

Por ejemplo, con listas grandes es mejor usar generadores porque no almacenan todo en RAM. Esto hace el código más eficiente, especialmente cuando trabajas con datos enormes o flujos infinitos. El generador "pausa" en cada `yield` y continúa desde ahí cuando lo pides.

**Evaluación de la IA — puntaje: 78/100**

- Coherente con la configuración (RF-11): ✅ sí

- **Fortalezas:**
  - Explicación clara y accesible de qué es un generador y su funcionamiento básico
  - Correcta identificación de `yield` como la palabra clave central que diferencia generadores de funciones comunes
  - Buena comprensión de la evaluación perezosa (lazy evaluation) y su ventaja en términos de memoria
  - Ejemplo contextualizado y relevante sobre listas grandes que demuestra comprensión práctica
  - Mención pertinente del concepto de 'pausa y continúa' que ilustra el funcionamiento interno
  - Tono apropiado para el nivel junior: directo y sin exceso de jerga

- **Errores:**
  - Imprecisión conceptual: dice que un generador 'crea un objeto que puedes iterar' sin mencionar explícitamente que es un iterador (debería haber sido más específico sobre el tipo de objeto)
  - No menciona la distinción entre generadores e iteradores de forma clara, cuando son conceptos relacionados pero distintos

- **Omisiones:**
  - No menciona el protocolo de iteración (__iter__ y __next__) que, aunque es avanzado para junior, enriquecería la respuesta
  - Falta un ejemplo de código concreto que muestre la diferencia práctica entre una función con return y un generador con yield
  - No explora otros beneficios además de memoria: mejor legibilidad del código, composición de operaciones
  - No menciona el objeto `generator` como tipo específico de Python o cómo inspeccionarlo
  - Ausencia de mención sobre cuándo NO usar generadores (situaciones donde necesitas acceso aleatorio)

- **Respuesta mejorada sugerida:**

  > Un generador es una función especial que usa `yield` en lugar de `return` para devolver valores uno a uno. Cuando llamas a un generador, no ejecuta el código inmediatamente; en su lugar, devuelve un objeto generador que implementa el protocolo de iteración.

**Diferencia fundamental:** Una función común calcula y retorna todos los resultados de una vez, almacenándolos en memoria. Un generador produce valores bajo demanda (evaluación perezosa), calculando cada valor solo cuando se solicita.

**Ejemplo:**
```python
# Función común: almacena todo en memoria
def numeros_funcion(n):
    resultado = []
    for i in range(n):
        resultado.append(i)
    return resultado

# Generador: produce valores bajo demanda
def numeros_generador(n):
    for i in range(n):
        yield i

# numeros_funcion(1000000) usa mucha RAM
# numeros_generador(1000000) usa casi nada
```

**Ventajas de memoria y eficiencia:**
- Consume mucha menos RAM al no almacenar todos los valores simultáneamente
- Mejor rendimiento en datos grandes o infinitos (como lecturas de archivos)
- Permite encadenación eficiente de operaciones
- Inicia la ejecución inmediatamente en lugar de calcular todo primero

Un generador es un tipo especial de iterador que pausa su ejecución en cada `yield` y continúa desde ese punto cuando se solicita el siguiente valor.

## Resultado general (RF-06)

- **Nivel estimado:** junior
- **Puntaje general (IA):** 78/100
- **Promedio calculado (ancla local):** 78.0/100
- **Áreas fuertes:**
  - Dominio de conceptos fundamentales: mutabilidad, inmutabilidad y diferencias entre estructuras de datos
  - Capacidad de explicar conceptos de forma clara y accesible, adecuada para el nivel junior
  - Comprensión sólida de casos de uso prácticos (tuplas como claves, listas para carrito de compras, generadores para memoria)
  - Identificación correcta de palabras clave y mecanismos: paréntesis vs corchetes, yield, tablas hash
  - Razonamiento lógico sobre por qué ciertas restricciones existen (inmutabilidad en claves, hashable, lazy evaluation)

- **Áreas de mejora:**
  - Profundizar en mecanismos internos: protocolos de iteración (__iter__, __next__), colisiones de hash, hashable como propiedad formal
  - Proporcionar ejemplos de código concreto: comparar función común vs generador con yield, métodos de lista (append, remove), creación de tuplas de un elemento
  - Distinguir claramente conceptos relacionados: generadores vs iteradores, características fundamentales de secuencias (ordenadas, indexables)
  - Explicar imprecisiones técnicas: la diferencia marginal de velocidad en tuplas, el hash como determinante de ubicación, no como 'puntero'
  - Considerar limitaciones y contexto: cuándo no usar generadores, mutabilidad de valores en diccionarios, complejidad temporal O(1) de búsquedas


## Plan de mejora personalizado (RF-07)

- Paso 1: Estudiar el protocolo de iteración de Python (__iter__, __next__) y la diferencia formal entre iterables, iteradores y generadores; practica creando un generador simple vs iterador personalizado
- Paso 2: Crear ejemplos de código concreto comparando: funciones con return vs generadores con yield, listas vs tuplas en operaciones reales, métodos mutables de listas (append, remove, extend)
- Paso 3: Investigar internals de Python: cómo funcionan las tablas hash, qué es 'hashable', colisiones de hash, complejidad temporal de diccionarios; ejecuta pequeños benchmarks de velocidad
- Paso 4: Practicar documentando casos de uso precisos: cuándo usar tuplas vs listas, cuándo un generador es overkill, restricciones reales en estructuras de datos; elabora un cheat sheet personal
- Paso 5: Resolver problemas de programación que combinen estas tres áreas (estructuras de datos, diccionarios y generadores) en escenarios juntos para consolidar comprensión integrada


## Trazabilidad de IA (RF-10 / RNF-05)

Se registraron **7 llamadas** a la IA (prompt exacto, respuesta cruda, modelo, criterios y fecha/hora). Muestra del prompt y respuesta de la primera llamada:

- **Tipo:** pregunta  |  **Modelo:** claude-haiku-4-5  |  **Versión prompt:** 1.0  |  **Fecha:** 2026-07-21T04:09:06.643681+00:00

```
SYSTEM PROMPT: Eres un asistente de práctica para entrevistas técnicas. Tu evaluación es una herramienta de estudio y práctica, NO una certificación oficial ni una garantía de resultado. NUNCA afirmes que la persona aprobará una entrevista real, será contratada, ni des garantías sobre procesos de reclutamiento reales. Respondes SIEMPRE con un único objeto JSON válido, sin texto antes ni después, sin [...]

USER PROMPT: Rol: Desarrollador Backend Tecnología: Python Nivel: junior Tipo de entrevista: conceptual Enfócate en conceptos y fundamentos teóricos. Redacta la pregunta en español. Aún no se ha realizado ninguna pregunta en esta sesión. Genera ahora la siguiente pregunta como un único objeto JSON.

RESPUESTA CRUDA: ```json { "pregunta": "Explica la diferencia entre una lista y una tupla en Python. ¿Cuáles son las principales características de cada una y en qué situaciones utilizarías una sobre la otra?", "dificultad": "junior", "criterios_evaluados": ["Comprensión de tipos de datos", "Mutabilidad vs inmutabilidad", "Casos de uso prácticos", "Características fundamentales"], "tema": "Estructuras de datos en Python" } ```
```


**Resumen de todas las trazas de esta entrevista:**

| # | Tipo | Modelo | Versión prompt | Fecha/hora |
|---|------|--------|----------------|------------|
| 1 | pregunta | claude-haiku-4-5 | 1.0 | 2026-07-21T04:09:06.643681+00:00 |
| 2 | evaluacion | claude-haiku-4-5 | 1.0 | 2026-07-21T04:09:21.224693+00:00 |
| 3 | pregunta | claude-haiku-4-5 | 1.0 | 2026-07-21T04:09:22.810820+00:00 |
| 4 | evaluacion | claude-haiku-4-5 | 1.0 | 2026-07-21T04:09:31.596758+00:00 |
| 5 | pregunta | claude-haiku-4-5 | 1.0 | 2026-07-21T04:09:33.563340+00:00 |
| 6 | evaluacion | claude-haiku-4-5 | 1.0 | 2026-07-21T04:09:43.864021+00:00 |
| 7 | resumen | claude-haiku-4-5 | 1.0 | 2026-07-21T04:09:51.964935+00:00 |
