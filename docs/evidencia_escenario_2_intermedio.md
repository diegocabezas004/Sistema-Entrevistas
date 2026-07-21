# Escenario 2 — Entrevista Intermedia (conceptual + práctica)

> ⚠️ Esta evaluación es una **herramienta de práctica**, no una certificación oficial ni garantía de contratación.

- **Entrevista ID:** 2
- **Rol:** Desarrollador Backend
- **Tecnología:** Python y APIs REST
- **Nivel configurado:** intermedio
- **Tipo:** mixta  |  **Idioma:** es
- **Cantidad de preguntas:** 3
- **Modelo IA:** claude-haiku-4-5
- **Estado:** completada

## Preguntas, respuestas y evaluación

### Pregunta 1 — Autorización y seguridad en APIs REST (dificultad: intermedio)

**Pregunta (IA):** Estás desarrollando una API REST en Python que gestiona pedidos de un e-commerce. Necesitas implementar un endpoint GET /pedidos/<id> que debe retornar los detalles de un pedido específico, pero solo si el usuario autenticado es el propietario del pedido o es administrador. Explica: 1) ¿Qué patrón o arquitectura usarías para manejar la autorización? 2) ¿Cómo implementarías la validación de permisos en tu código? 3) ¿Qué códigos HTTP devolverías en cada caso (usuario autorizado, no autorizado, no autenticado, pedido no encontrado)? 4) Menciona al menos dos riesgos de seguridad comunes en este tipo de implementaciones y cómo prevenirlos.

**Criterios evaluados:** Comprensión de patrones de autorización en APIs, Implementación de control de acceso basado en roles (RBAC), Conocimiento de códigos HTTP y semántica REST, Conciencia sobre vulnerabilidades de seguridad comunes, Capacidad de diseñar soluciones escalables y mantenibles

**Respuesta del candidato:**

> Usaría un patrón de **decoradores con middleware de autenticación**. 

Para la implementación, crearía un decorador que verifique el JWT del usuario y luego valide permisos dentro del endpoint:

```python
@app.route('/pedidos/<id>')
@token_required
def get_pedido(id):
    pedido = Pedido.query.get(id)
    if not pedido:
        return {"error": "No encontrado"}, 404
    
    if current_user.id != pedido.user_id and not current_user.is_admin:
        return {"error": "Acceso denegado"}, 403
    
    return pedido.to_dict(), 200
```

**Códigos HTTP:**
- 200: Autorizado
- 401: No autenticado
- 403: Autenticado pero sin permisos
- 404: Pedido no existe

**Riesgos de seguridad:**
1. **Enumeration attack**: Devolver 403 vs 404 diferente revela si el pedido existe. Soluciono devolviendo 404 siempre si no tiene acceso.
2. **Insecure Direct Object Reference**: Validar siempre el propietario, no confiar en el ID del URL.

**Evaluación de la IA — puntaje: 78/100**

- Coherente con la configuración (RF-11): ✅ sí

- **Fortalezas:**
  - Identificación correcta del patrón de decoradores para separar concerns de autenticación
  - Implementación clara y funcional del flujo de autorización con validación de rol
  - Correcta asignación de códigos HTTP (200, 401, 403, 404) con semántica REST apropiada
  - Reconocimiento de dos vulnerabilidades reales y críticas (enumeration attack e IDOR)
  - Propuesta pragmática para mitigar enumeration attack devolviendo 404 consistentemente
  - Código legible y estructura lógica fácil de seguir
  - Mención explícita de la importancia de validar el propietario del recurso

- **Errores:**
  - No especifica cómo implementar el decorador @token_required ni cómo se obtiene current_user
  - La solución de enumeration attack (devolver 404 siempre) es debatible: sacrifica experiencia de usuario y la mayoría de APIs REST modernas usan 403; falta analizar trade-offs
  - No menciona RBAC explícitamente aunque lo implementa; un nivel intermedio debe nombrarlo como patrón
  - Falta manejo de excepciones o errores en la consulta a base de datos (ej: Pedido.query.get puede fallar)
  - No aborda JWT refresh tokens ni expiración de tokens en el contexto de autenticación

- **Omisiones:**
  - No explica qué framework REST usa (Flask, Django, FastAPI) ni cómo varía la implementación
  - Falta mencionar validación de entrada del parámetro 'id' (inyección SQL, tipos de dato inválidos)
  - No incluye logging/auditoría de intentos de acceso no autorizado, importante para seguridad en nivel intermedio
  - No menciona rate limiting para prevenir abuso de enumeración de IDs
  - Ausencia de documentación sobre cómo estructurar permisos en la BD (roles, relaciones user-pedido)
  - No aborda caching y sus implicaciones de seguridad en GET
  - No menciona testing de casos de seguridad (test negativo para validar restricciones)

- **Respuesta mejorada sugerida:**

  > Usaría un patrón de **decoradores con middleware de autenticación** combinado con **RBAC (Control de Acceso Basado en Roles)**.

**Implementación mejorada:**

```python
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return {"error": "Token no proporcionado"}, 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuario.query.get(data['user_id'])
            if not current_user:
                return {"error": "Usuario no encontrado"}, 401
        except jwt.ExpiredSignatureError:
            return {"error": "Token expirado"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Token inválido"}, 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/pedidos/<int:pedido_id>', methods=['GET'])
@token_required
def get_pedido(current_user, pedido_id):
    # Validación de entrada
    if not isinstance(pedido_id, int) or pedido_id <= 0:
        return {"error": "ID de pedido inválido"}, 400
    
    try:
        pedido = Pedido.query.get(pedido_id)
    except Exception as e:
        current_app.logger.error(f"Error DB: {str(e)}")
        return {"error": "Error interno del servidor"}, 500
    
    # No distinguir entre "no existe" y "sin acceso" para prevenir enumeration
    if not pedido or (pedido.user_id != current_user.id and not current_user.is_admin):
        # Log de intento no autorizado
        current_app.logger.warning(f"Acceso denegado a pedido {pedido_id} por usuario {current_user.id}")
        return {"error": "Recurso no encontrado o acceso denegado"}, 404
    
    return pedido.to_dict(), 200
```

**Códigos HTTP:**
- 200: Pedido encontrado y autorizado
- 400: Parámetro de entrada inválido
- 401: No autenticado o token expirado
- 404: Pedido no existe o sin permisos (unificado para seguridad)
- 500: Error servidor

**Riesgos de seguridad y mitigación:**

1. **Enumeration Attack / Information Disclosure**: Diferencia entre 403 y 404 revela existencia de pedidos. *Solución*: Retornar 404 en ambos casos o usar mensajes genéricos. Trade-off: reduce claridad para client pero mejora seguridad.

2. **Insecure Direct Object Reference (IDOR)**: Validar siempre que current_user sea propietario. *Solución*: Nunca confiar en ID de URL; verificar relación user-pedido en BD.

3. **Adicionales**: 
   - Validar tipo y rango del parámetro id
   - Implementar rate limiting en endpoint
   - Auditar intentos de acceso rechazados
   - Manejar excepciones de BD explícitamente

**Consideraciones arquitectónicas:**
- Framework: En FastAPI usarías Depends() para inyección de dependencias; en Django class-based views con decoradores de permisos
- Escalabilidad: Para muchos usuarios, considerar caché (Redis) con invalidación segura
- Testing: Tests negativos para validar rechazos de acceso

### Pregunta 2 — Concurrencia, idempotencia y resiliencia en APIs REST (dificultad: intermedio)

**Pregunta (IA):** Estás diseñando una API REST en Python que procesa pagos y necesita manejar concurrencia. Imagina que dos usuarios intentan realizar una transacción sobre la misma cuenta simultáneamente. Explica: 1) ¿Qué problemas de concurrencia podrían ocurrir (race conditions, deadlocks)? 2) ¿Qué mecanismos (locks, transacciones, versionado optimista) usarías para prevenirlos en tu base de datos y por qué? 3) ¿Cómo implementarías idempotencia en el endpoint POST /transacciones para evitar duplicados si el cliente reintenta la solicitud? 4) ¿Qué patrones de reintento usarías en el cliente y cómo los combinarías con los códigos HTTP de respuesta?

**Criterios evaluados:** Comprensión de problemas de concurrencia en sistemas distribuidos, Conocimiento de mecanismos de sincronización y control transaccional, Implementación de idempotencia en APIs, Diseño de estrategias de reintentos y manejo de errores, Aplicación de patrones de resiliencia en APIs REST

**Respuesta del candidato:**

> Buena pregunta. Voy a abordarla por partes:

1) **Problemas**: Principalmente race conditions. Dos transacciones leen el saldo simultáneamente, ambas creen que hay fondos, y se ejecutan ambas dejando el saldo negativo. Deadlocks son menos comunes en este escenario.

2) **Mecanismos**: Usaría **transacciones ACID con locks pesimistas** (SELECT FOR UPDATE) porque es crítico en pagos. Básicamente: adquiero lock en la fila, valido saldo, ejecuto transacción. Es más seguro que optimista aquí. Alternativa: versionado optimista si tengo baja contención.

3) **Idempotencia**: Genero un `idempotency_key` único por cliente (UUID), lo almaceno en BD. En POST /transacciones, chequeo si ya existe esa key. Si existe, retorno el resultado previo sin procesar de nuevo.

4) **Reintentos cliente**: Uso exponential backoff (1s, 2s, 4s...) con jitter. Reintento en 409, 503, 5xx. En 400, 401, 422 no reintento. Siempre con el mismo `idempotency_key`.

**Evaluación de la IA — puntaje: 78/100**

- Coherente con la configuración (RF-11): ✅ sí

- **Fortalezas:**
  - Identifica correctamente la race condition como problema principal en transacciones concurrentes sobre la misma cuenta
  - Demuestra comprensión sólida de SELECT FOR UPDATE como mecanismo de lock pesimista en bases de datos
  - Explica adecuadamente el flujo de adquisición de lock, validación y ejecución en transacciones críticas
  - Implementa idempotencia con idempotency_key de forma correcta y práctica, almacenando en base de datos
  - Distingue correctamente entre códigos HTTP: reintentos en 409, 503, 5xx y no reintenta en 400, 401, 422
  - Aplica exponential backoff con jitter, demostrando conocimiento de patrones modernos de resiliencia
  - Estructura la respuesta de forma clara y ordenada, abordando cada punto solicitado

- **Errores:**
  - Afirma que deadlocks son 'menos comunes' en este escenario, cuando en realidad podrían ocurrir si hay múltiples locks en diferentes órdenes en operaciones relacionadas
  - No menciona el nivel de aislamiento de la transacción (SERIALIZABLE vs READ_COMMITTED), crucial para garantizar que SELECT FOR UPDATE sea efectivo
  - No aclara cómo se almacena y recupera el resultado previo de idempotencia (¿retorna solo el estado o también datos de respuesta?)
  - Simplifica demasiado el manejo de idempotency_key sin mencionar tiempo de expiración (TTL) ni problemas de sincronización en sistemas distribuidos

- **Omisiones:**
  - No menciona bases de datos distribuidas o replicación, donde las transacciones ACID pueden ser más complejas
  - Falta explicación sobre cómo implementar idempotencia en la capa de aplicación Python (ej: decoradores, middleware, ORM features)
  - No aborda conflictos entre reintentos cliente y transacciones parcialmente completadas (ej: pago procesado pero respuesta perdida)
  - No discute monitoring, logging o métricas para detectar race conditions en producción
  - Omite mencionar que algunos códigos HTTP como 408 (timeout) también podrían justificar reintentos

- **Respuesta mejorada sugerida:**

  > 1) **Problemas de concurrencia**: La race condition descrita es correcta. Adicionalmente, en sistemas distribuidos con replicación podrían ocurrir anomalías incluso con locks si el nivel de aislamiento es débil. Los deadlocks pueden ocurrir si diferentes transacciones adquieren locks en distinto orden sobre múltiples filas.

2) **Mecanismos**: En Python con SQLAlchemy/psycopg2, usaría transacciones ACID con **SELECT FOR UPDATE** en aislamiento READ_COMMITTED (o SERIALIZABLE si es crítico). Ejemplo:
```
with db.transaction():
    account = db.query(Account).filter(Account.id==account_id).with_for_update().first()
    if account.balance < amount: raise InsufficientFunds()
    account.balance -= amount
    db.commit()
```
El versionado optimista (columna version con incremento) es alternativa si baja contención, reintentando operación completa en conflicto.

3) **Idempotencia**: Almacenar idempotency_key con hash de parámetros y resultado. En el endpoint:
```python
key = request.headers.get('Idempotency-Key')
if cached := cache.get(key):
    return cached
result = process_transaction(...)
cache.set(key, result, ttl=3600)
return result
```
Garante que reintentos retornen exactamente el mismo resultado sin duplicar transacciones.

4) **Reintentos cliente**: Exponential backoff (1s, 2s, 4s, 8s) con jitter. Reintentable: 408, 409, 429, 503, 504, 5xx. No reintentable: 400, 401, 403, 404, 422. Siempre con idempotency_key para garantizar idempotencia extremo-a-extremo. Establecer max_retries=3 y timeout adaptativo.

### Pregunta 3 — Optimización de consultas y rendimiento en APIs REST con relaciones complejas (dificultad: intermedio)

**Pregunta (IA):** Estás desarrollando una API REST en Python que expone datos de un sistema complejo con múltiples relaciones entre entidades (usuarios, productos, categorías, inventario). Un cliente solicita un endpoint GET /productos/<id> que debe retornar el producto con sus categorías relacionadas, el inventario disponible, y reseñas de usuarios. Sin embargo, observas que las consultas son lentas y generan múltiples viajes a la base de datos. Explica: 1) ¿Qué problema de rendimiento específico estás experimentando y cómo se llama en el contexto de ORMs? 2) ¿Qué estrategias de carga (eager loading, lazy loading, select_in_load) implementarías y por qué? 3) ¿Cómo estructurarías la respuesta JSON (flat, nested, o links HATEOAS) y qué ventajas y desventajas tiene cada enfoque? 4) ¿Implementarías paginación o filtrado en las reseñas dentro de esta respuesta? ¿Por qué es importante y cómo lo harías? 5) ¿Qué mecanismos de caché (HTTP caching headers, Redis) podrías agregar y cuáles serían sus implicaciones para datos que cambian frecuentemente?

**Criterios evaluados:** Comprensión del problema N+1 en ORMs, Estrategias de optimización de consultas (eager loading, lazy loading), Diseño de respuestas JSON y consideraciones de API REST, Paginación y filtrado en relaciones, Implementación de caché en APIs REST, Trade-offs entre rendimiento, complejidad y mantenibilidad

**Respuesta del candidato:**

> **1) Problema: N+1 queries**
Estoy experimentando el problema clásico N+1. Cuando cargo un producto, se ejecuta 1 query. Luego, al acceder a categorías, inventario y reseñas, se generan queries adicionales para cada relación. Con SQLAlchemy, se llama "lazy loading" por defecto.

**2) Estrategias de carga:**
Usaría `selectinload()` o `joinedload()` para eager loading. `selectinload()` es mejor aquí porque evita duplicados en joins complejos con múltiples relaciones. Lo haría así:
```python
producto = session.query(Producto).options(
    selectinload(Producto.categorias),
    selectinload(Producto.inventario),
    selectinload(Producto.resenas)
).filter_by(id=id).first()
```

**3) Estructura JSON:**
Iría por **nested** inicialmente:
- Ventaja: Una sola request, datos contextuales claros
- Desventaja: respuesta pesada, difícil cachear parcialmente

Consideraría **links HATEOAS** si crece: permite que el cliente solicite reseñas por separado.

**4) Paginación en reseñas:**
Sí, definitivamente. Las reseñas pueden ser muchas. Incluiría `?pagina=1&limite=10` en la query, no las cargó todas en el producto principal.

**5) Caché:**
Redis para datos estables (producto + categorías). HTTP headers (`Cache-Control: max-age=300`) para

**Evaluación de la IA — puntaje: 72/100**

- Coherente con la configuración (RF-11): ✅ sí

- **Fortalezas:**
  - Identificación correcta del problema N+1 queries y su naturaleza en SQLAlchemy
  - Conocimiento técnico sólido de selectinload() vs joinedload() con justificación apropiada (evitar duplicados)
  - Código de ejemplo funcional y bien estructurado usando options()
  - Comprensión del trade-off entre nested vs HATEOAS y cuándo aplicar cada uno
  - Reconocimiento de la importancia de paginar reseñas para respuestas pesadas
  - Mención de estrategias de caché tanto a nivel HTTP como Redis

- **Errores:**
  - Afirmación imprecisa: 'selectinload() es mejor aquí porque evita duplicados' - selectinload() ejecuta múltiples queries, mientras que joinedload() puede causar duplicados con one-to-many. La razón correcta es que selectinload() es más eficiente para múltiples relaciones independientes
  - Confusión en el alcance del caché: sugiere Redis para 'producto + categorías' sin aclarar qué datos cambian frecuentemente y cuál es la invalidación
  - Falta de implementación concreta de paginación en reseñas: propone `?pagina=1&limite=10` pero no muestra cómo separar esa lógica del eager loading principal

- **Omisiones:**
  - No menciona la estrategia de cargar solo las reseñas paginadas en la respuesta principal (distinct() con selectinload en casos complejos)
  - Ausencia de discusión sobre contains_eager() para paginar relaciones dentro de un solo query
  - No aborda cómo manejar la respuesta cuando reseñas se cargan paginadas vs completas (rompe el contrato de la API)
  - Falta de detalles sobre estrategia de invalidación de caché (TTL, eventos de cambio, cache busting)
  - No explica implicaciones de usar Redis en datos que cambian frecuentemente (edad del caché, consistencia eventual)
  - Omite consideración de compresión gzip en respuestas nested grandes
  - No menciona alternativas como GraphQL para evitar over-fetching vs under-fetching

- **Respuesta mejorada sugerida:**

  > **1) Problema: N+1 queries**
Experimenta el problema N+1 queries clásico. Al cargar un producto, se ejecuta 1 query base. Luego, acceder a cada relación (categorías, inventario, reseñas) genera queries adicionales por cada acceso a una colección. En SQLAlchemy, lazy loading por defecto es `'select'`, que dispara queries individuales.

**2) Estrategias de carga:**
Usaría `selectinload()` para categorías e inventario (relaciones independientes y pequeñas):
```python
producto = session.query(Producto).options(
    selectinload(Producto.categorias),
    selectinload(Producto.inventario)
).filter_by(id=id).first()
```

Para reseñas, NO usaría eager loading completo. En su lugar, las cargaría paginadas en un endpoint separado o como relación lazy pero con caché:
```python
@app.get('/productos/{id}/resenas?pagina=1&limite=10')
def get_resenas_paginadas(id, pagina, limite):
    # Query separada con paginación
```

**Razonamiento:** selectinload() ejecuta N+1 queries pero evita duplicación de filas (problema de joinedload con one-to-many). joinedload() reduciría a 1 query pero multiplicaría filas si hay múltiples categorías.

**3) Estructura JSON:**
Estrctura **nested parcial**:
```json
{
  "id": 1,
  "nombre": "Laptop",
  "categorias": [{"id": 5, "nombre": "Electrónica"}],
  "inventario": {"cantidad": 15, "almacen": "A1"},
  "resenas": {
    "pagina": 1,
    "total": 50,
    "items": [{"id": 1, "usuario": "..."}],
    "siguiente": "/productos/1/resenas?pagina=2"
  }
}
```
Ventajas: Una request, contexto claro. Desventajas: respuesta pesada, reseñas deben paginarse.

**4) Paginación en reseñas:**
Sí, esencial. Las reseñas se cargan en endpoint separado o como sub-recurso:
```python
@app.get('/productos/{id}/resenas')
def get_resenas(id: int, pagina: int = 1, limite: int = 10):
    skip = (pagina - 1) * limite
    resenas = session.query(Resena).filter_by(producto_id=id).offset(skip).limit(limite).all()
    return {"items": resenas, "pagina": pagina, "total": count}
```
No cargas todas con selectinload(); la respuesta sería inmanejable y caché ineficiente.

**5) Caché:**
**Para datos estables (producto + categorías):** HTTP headers `Cache-Control: max-age=3600, public` + ETags.
**Para inventario (cambia frecuentemente):** `Cache-Control: max-age=60` o sin caché.
**Para reseñas:** Redis con TTL de 5 minutos + invalidación al agregar reseña:
```python
from redis import Redis
r = Redis()
key = f'product:{id}:reviews:page:{pagina}'
if not r.get(key):
    resenas = db.query(Resena)...
    r.setex(key, 300, json.dumps(resenas))
```
Invalidación: `r.delete(f'product:{id}:reviews:*')` al crear/actualizar reseña.

**Trade-offs:** Caché agresivo = respuestas rápidas pero datos potencialmente obsoletos. Redis añade complejidad operacional.

## Resultado general (RF-06)

- **Nivel estimado:** intermedio
- **Puntaje general (IA):** 76/100
- **Promedio calculado (ancla local):** 76.0/100
- **Áreas fuertes:**
  - Comprensión sólida de patrones de seguridad en APIs REST (RBAC, autorización con decoradores)
  - Identificación correcta de vulnerabilidades reales (IDOR, enumeration attacks)
  - Conocimiento técnico de mecanismos de concurrencia (SELECT FOR UPDATE, locks pesimistas)
  - Implementación práctica de idempotencia con idempotency_key en transacciones
  - Manejo apropiado de códigos HTTP REST con semántica correcta
  - Dominio de patrones modernos de resiliencia (exponential backoff con jitter)
  - Identificación del problema N+1 queries en SQLAlchemy
  - Distinción técnica entre estrategias de carga (selectinload vs joinedload)
  - Capacidad para estructurar respuestas considerando trade-offs (nested vs HATEOAS)

- **Áreas de mejora:**
  - Precisión técnica: confusión sobre cuándo selectinload evita duplicados vs cuándo joinedload los causa
  - Nivel de aislamiento de transacciones: no menciona SERIALIZABLE vs READ_COMMITTED en contexto de concurrencia
  - Implementación de detalles: falta cómo obtener current_user en decoradores, almacenamiento y recuperación de resultados idempotentes
  - Trade-offs de seguridad: no analiza pros y contras de devolver 404 vs 403 para enumeration attacks
  - Validación de entrada: ausencia de validación de tipos y detección de inyección SQL en parámetros
  - Auditoría y observabilidad: no menciona logging, rate limiting ni métricas para detectar problemas en producción
  - Invalidación de caché: falta estrategia concreta (TTL, eventos, cache busting) para datos que cambian frecuentemente
  - Paginación compleja: no explica cómo paginar relaciones dentro de un single query (contains_eager)
  - Consideraciones en sistemas distribuidos: ausencia de análisis sobre replicación y transacciones ACID distribuidas


## Plan de mejora personalizado (RF-07)

- Paso 1: Profundizar en niveles de aislamiento de transacciones SQL (READ_UNCOMMITTED, READ_COMMITTED, REPEATABLE_READ, SERIALIZABLE) y cómo elegir según el escenario; laboratorio práctico: reproducir race conditions con distintos niveles
- Paso 2: Dominar estrategias de carga en SQLAlchemy con casos reales: crear ejemplos con selectinload(), joinedload(), contains_eager() para diferentes topologías de relaciones (one-to-many, many-to-many); analizar planes de ejecución SQL generados
- Paso 3: Implementar validación exhaustiva: usar Pydantic para validar tipos de entrada, sanitizar parámetros contra inyección SQL, implementar validación en múltiples capas (modelo, servicio, controlador)
- Paso 4: Diseñar un sistema completo de caché: implementar Redis con invalidación basada en TTL y eventos; comparar consistencia inmediata vs eventual; laboratorio: medir impacto en latencia y tasa de acierto
- Paso 5: Agregar observabilidad a APIs: implementar logging estructurado de intentos de acceso no autorizado, rate limiting por usuario/IP, métricas de race conditions detectadas; usar herramientas como Prometheus y ELK
- Paso 6: Estudiar idempotencia en sistemas distribuidos: entender sincronización de idempotency_key, TTL de resultados almacenados, manejo de respuestas perdidas; laboratorio: simular desconexiones y reintentoscon redes no confiables
- Paso 7: Práctica guiada: desarrollar un endpoint completo que integre seguridad, concurrencia, rendimiento y caché; luego refactorizarlo basado en feedback de revisión de código
- Paso 8: Estudiar alternativas a REST (GraphQL) para entender cuándo evita over-fetching/under-fetching; comparar con enfoque tradicional en casos reales de tu dominio


## Trazabilidad de IA (RF-10 / RNF-05)

Se registraron **7 llamadas** a la IA (prompt exacto, respuesta cruda, modelo, criterios y fecha/hora). Muestra del prompt y respuesta de la primera llamada:

- **Tipo:** pregunta  |  **Modelo:** claude-haiku-4-5  |  **Versión prompt:** 1.0  |  **Fecha:** 2026-07-21T04:09:55.366395+00:00

```
SYSTEM PROMPT: Eres un asistente de práctica para entrevistas técnicas. Tu evaluación es una herramienta de estudio y práctica, NO una certificación oficial ni una garantía de resultado. NUNCA afirmes que la persona aprobará una entrevista real, será contratada, ni des garantías sobre procesos de reclutamiento reales. Respondes SIEMPRE con un único objeto JSON válido, sin texto antes ni después, sin [...]

USER PROMPT: Rol: Desarrollador Backend Tecnología: Python y APIs REST Nivel: intermedio Tipo de entrevista: mixta Puedes combinar teoría, práctica y diseño. Redacta la pregunta en español. Aún no se ha realizado ninguna pregunta en esta sesión. Genera ahora la siguiente pregunta como un único objeto JSON.

RESPUESTA CRUDA: ```json { "pregunta": "Estás desarrollando una API REST en Python que gestiona pedidos de un e-commerce. Necesitas implementar un endpoint GET /pedidos/<id> que debe retornar los detalles de un pedido específico, pero solo si el usuario autenticado es el propietario del pedido o es administrador. Explica: 1) ¿Qué patrón o arquitectura usarías para manejar la autorización? 2) ¿Cómo implementarías la validación de permisos en tu código? 3) ¿Qué códigos HTTP devolverías en cada caso (usuario [...]
```


**Resumen de todas las trazas de esta entrevista:**

| # | Tipo | Modelo | Versión prompt | Fecha/hora |
|---|------|--------|----------------|------------|
| 1 | pregunta | claude-haiku-4-5 | 1.0 | 2026-07-21T04:09:55.366395+00:00 |
| 2 | evaluacion | claude-haiku-4-5 | 1.0 | 2026-07-21T04:10:11.690171+00:00 |
| 3 | pregunta | claude-haiku-4-5 | 1.0 | 2026-07-21T04:10:15.109906+00:00 |
| 4 | evaluacion | claude-haiku-4-5 | 1.0 | 2026-07-21T04:10:29.546000+00:00 |
| 5 | pregunta | claude-haiku-4-5 | 1.0 | 2026-07-21T04:10:34.144400+00:00 |
| 6 | evaluacion | claude-haiku-4-5 | 1.0 | 2026-07-21T04:10:52.904295+00:00 |
| 7 | resumen | claude-haiku-4-5 | 1.0 | 2026-07-21T04:11:03.375080+00:00 |
