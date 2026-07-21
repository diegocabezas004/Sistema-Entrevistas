# Escenario 3 — Arquitectura / Resolución de problemas (diseño)

> ⚠️ Esta evaluación es una **herramienta de práctica**, no una certificación oficial ni garantía de contratación.

- **Entrevista ID:** 3
- **Rol:** Arquitecto de Software
- **Tecnología:** Sistemas distribuidos
- **Nivel configurado:** senior
- **Tipo:** arquitectura  |  **Idioma:** es
- **Cantidad de preguntas:** 2
- **Modelo IA:** claude-haiku-4-5
- **Estado:** completada

## Preguntas, respuestas y evaluación

### Pregunta 1 — Diseño arquitectónico de sistemas distribuidos con restricciones de consistencia y disponibilidad (dificultad: senior)

**Pregunta (IA):** Estás diseñando una plataforma de comercio electrónico global que debe procesar millones de transacciones diarias con latencia mínima y garantizar consistencia eventual de datos de inventario. ¿Cómo abordarías la tensión entre consistencia fuerte y disponibilidad en este sistema? Describe tu estrategia de particionamiento de datos, sincronización entre regiones geográficas y el patrón de comunicación que utilizarías entre servicios de pago, inventario y notificaciones. ¿Qué compromisos harías y por qué?

**Criterios evaluados:** Comprensión del teorema CAP y aplicación a contextos reales, Diseño de estrategias de particionamiento y replicación, Gestión de consistencia eventual en sistemas distribuidos, Decisiones arquitectónicas basadas en trade-offs, Conocimiento de patrones de comunicación asíncrona, Escalabilidad horizontal y tolerancia a fallos

**Respuesta del candidato:**

> Elegiría **eventual consistency con transacciones locales fuertes**. El pago es crítico: procesaría en una región primaria con replicación síncrona a standby, aceptando latencia controlada. Inventario usaría sharding por geografía —cada región tiene su vista local, sincronizando cambios vía event sourcing asíncrono.

Para particionamiento: sharding por región + tenant ID, evitando hot spots. Entre regiones, usaría message queues (Kafka) con idempotencia garantizada —cuando falla replicación, reintentos no duplican reservas.

Patrón: pago → evento persistido → cola → inventario actualiza local → notificaciones. Si hay divergencia, aceptaré inconsistencia temporal (24h máximo) antes que bloquear ventas.

El trade-off consciente: disponibilidad sobre consistencia fuerte. Una transacción rechazada es peor que sobrestock eventual. Monitoreo activo detecta desviaciones.

**Evaluación de la IA — puntaje: 78/100**

- Coherente con la configuración (RF-11): ✅ sí

- **Fortalezas:**
  - Demuestra comprensión sólida del teorema CAP y su aplicación práctica: elige disponibilidad sobre consistencia fuerte de forma justificada
  - Propone sharding por región + tenant ID, estrategia apropiada para e-commerce global que considera hot spots
  - Utiliza event sourcing asíncrono con Kafka, patrón maduro y reconocido para sincronización entre regiones
  - Identifica correctamente la criticidad diferenciada: consistencia fuerte en pagos (core), eventual en inventario (aceptable)
  - Menciona idempotencia explícitamente, requisito fundamental para garantizar no-duplicación en reintentos
  - Cuantifica el horizonte de inconsistencia (24h máximo), decisión consciente con viabilidad comercial
  - Estructura clara del flujo: pago → evento → cola → inventario → notificaciones

- **Errores:**
  - Afirma 'replicación síncrona a standby' para pagos sin aclarar la latencia real que introduce: contradice ligeramente el énfasis en 'latencia mínima'
  - No aborda explícitamente cómo garantizar la idempotencia en el lado del consumidor de eventos (solo la menciona en contexto de reintentos)
  - Omite detalles sobre coordinación distribuida ante fallos: ¿qué ocurre si Kafka entrega el evento pero inventario no procesa? ¿Dead letter queues?
  - No menciona estrategia de rollback o compensación transaccional para manejar inconsistencias detectadas

- **Omisiones:**
  - Falta análisis explícito de conflict resolution cuando dos regiones actualizan inventario simultáneamente (p.ej., último ítem desde dos geografías)
  - No detalla mecanismo de monitoreo 'activo' mencionado: ¿checksums, auditoría eventual, reconciliación batch?
  - Ausencia de consideración sobre latencia de propagación entre regiones y su impacto en ventana de sobrestock/insuficiencia
  - No discute patrón CQRS explícitamente, aunque el diseño lo sugiere (consistencia eventual en read models de inventario)
  - Omite validación de decisiones: ¿testing de partición de red? ¿chaos engineering?
  - Falta mencionar SLA diferenciados por región o por tipo de servicio (pagos vs. notificaciones)

- **Respuesta mejorada sugerida:**

  > Elegiría **eventual consistency con transacciones locales fuertes**, pero con matices clave:

**Modelo de consistencia**: Pago en región primaria con replicación asíncrona a standby (no síncrona, ya que latencia es crítica). Write-ahead logging garantiza durabilidad local antes de responder al cliente. Inventario usa eventual consistency con horizonte de 24h máximo.

**Particionamiento**: Sharding por región geográfica + tenant ID. Para evitar hot spots: bucket adicional para productos de alta demanda (distributed counter usando Redis con eventual consistency).

**Sincronización entre regiones**:
- Eventos inmutables persistidos en cada región en local event store
- Kafka con replicación cross-region con garantía at-least-once
- Consumidores idempotentes: key = (evento_id, región) para detectar duplicados antes de aplicar
- Dead letter queues para eventos fallidos, análisis manual post-mortem

**Patrón comunicación**: Event sourcing + CQRS implícito
1. Pago crea evento "PaymentAuthorized" → persiste localmente
2. Evento entra en Kafka con timestamp y región origen
3. Inventario consume: verifica idempotencia (cache local), resta stock, emite "StockReserved"
4. Notificación consume ambos eventos de forma eventual

**Manejo de divergencias**:
- Reconciliación scheduled (diaria): checksum por tenant de inventario global vs. suma de vistas locales
- Si divergencia > threshold: trigger compensación (ajuste de stock) + alert
- Conflict resolution: last-write-wins con vector clocks por región

**Trade-offs explícitos**:
- Escojo disponibilidad sobre consistencia fuerte porque rechazar pagos de clientes globales es inaceptable
- Acepto sobrestock temporal: costo operativo < costo de indisponibilidad
- Latencia de sincronización asíncrona (segundos a minutos) es tolerable para inventario, pero pagos tienen timeout local de 30s

**Observabilidad y resiliencia**:
- Distributed tracing (Jaeger) en evento root → seguimiento de propagación
- Circuit breakers entre servicios
- Pruebas de chaos: simular partición de red Kafka, fallos de standby, eventos fuera de orden

### Pregunta 2 — Arquitectura resiliente y distribuida con manejo de fallos en cascada (dificultad: senior)

**Pregunta (IA):** Estás arquitectando un sistema de microservicios para una plataforma de streaming de video en tiempo real con millones de usuarios concurrentes distribuidos globalmente. El desafío es mantener la sincronización de estado de sesión, evitar divergencia de datos críticos entre regiones, y garantizar que los fallos en cascada no afecten todo el sistema. ¿Cómo diseñarías la topología de comunicación entre servicios (síncrona vs asíncrona)? ¿Qué patrones de resiliencia implementarías (circuit breaker, timeout, retry, bulkhead)? ¿Cómo manejarías la consistencia de datos de sesión y metadatos de usuarios entre múltiples centros de datos? ¿Cuál sería tu estrategia de observabilidad para detectar y mitigar fallos distribuidos?

**Criterios evaluados:** Diseño de topología de comunicación en sistemas distribuidos, Patrones de resiliencia y tolerancia a fallos, Gestión de consistencia de datos entre regiones, Estrategia de observabilidad y monitoreo distribuido, Análisis de trade-offs arquitectónicos, Conocimiento de patrones avanzados (saga, event sourcing, CQRS)

**Respuesta del candidato:**

> Usaría un híbrido: **síncrono para operaciones críticas** (autenticación, billing) con gRPC y **asíncrono para eventos** (reproducción, métricas) vía Kafka. Así aíslo latencias.

Para resiliencia: **circuit breaker + timeout agresivo** (500ms máx), **retry exponencial solo en idempotentes**, **bulkheads por tenant** para evitar que un usuario saturado derrumbe otros.

En consistencia: **eventual consistency** para sesión con **event sourcing** desde región primaria. Cachés locales en cada región con TTL corto (30s), fallos degradan a versión stale. Critical data (billing) requiere escritura síncrona al primary.

Observabilidad: **distributed tracing** (Jaeger), **métricas por servicio** (Prometheus), **alertas en latencia p99** y **error rate**. Logs estructurados con correlation IDs. Detecto cascadas monitoreando **fanout requests** y **queue depth**.

**Evaluación de la IA — puntaje: 72/100**

- Coherente con la configuración (RF-11): ✅ sí

- **Fortalezas:**
  - Propone arquitectura híbrida bien fundamentada: síncrono para operaciones críticas con gRPC, asíncrono para eventos con Kafka, demostrando comprensión de trade-offs latencia vs acoplamiento
  - Implementación de patrones de resiliencia múltiples y coordinados: circuit breaker, timeout, retry exponencial condicional, bulkheads por tenant (aislamiento por dominio de negocio)
  - Estrategia de consistencia sofisticada diferenciada por criticidad: eventual consistency + event sourcing para sesiones, escritura síncrona a primaria para billing
  - Caché distribuida con TTL inteligente y degradación controlada a datos stale en fallos
  - Stack de observabilidad coherente: Jaeger para trazas distribuidas, Prometheus para métricas, correlation IDs para traceabilidad end-to-end
  - Monitoreo proactivo de síntomas de cascada: fanout requests y queue depth
  - Demuestra pensamiento en niveles de severidad operacional (crítico vs no-crítico)

- **Errores:**
  - Timeout de 500ms es extremadamente agresivo para streaming de video global con latencia de WAN intercontinental; sin justificar, genera riesgo alto de falsos positivos y reintentos innecesarios
  - No especifica arquitectura de replicación de estado entre regiones (master-slave, multi-master, quorum) ni cómo resuelve conflictos geográficos
  - Event sourcing mencionado superficialmente sin abordar immutabilidad, snapshots, o cómo mantiene log distribuido consistente
  - TTL de 30s en cachés locales es muy corto para sesiones de video en tiempo real; riesgo de invalidación excesiva durante streaming
  - No menciona mecanismo explícito de consenso (raft, paxos) para metadata crítica ni cómo resuelve split-brain entre datacenters
  - Bulkheads 'por tenant' es vago; no especifica si son a nivel de conexión, threads, CPU o memoria
  - No aborda explícitamente SLA por región, priorización de tráfico en degradación (video vs billing) ni strategic failover

- **Omisiones:**
  - Ausencia de discusión sobre patrón Saga para transacciones distribuidas entre microservicios (especialmente en billing crítico)
  - No menciona CQRS para separación lectura/escritura en sesiones, optimizando proyecciones por región
  - Falta especificar tecnología para state management distribuido (Redis con Sentinel, Consul, etcd) para sesiones entre instancias
  - No aborda latency budget end-to-end: desglose de presupuesto de 500ms entre hops de red, procesamiento, I/O
  - Omite discusión sobre backpressure y throttling en Kafka para evitar acumulación en queues de eventos
  - No menciona estrategia de canary deployments o feature flags para mitigar riesgos de cambios en topología de comunicación
  - Falta análisis de rate limiting global (token bucket distribuido) para proteger servicios downstream
  - No especifica cómo maneja desincronización temporal entre regiónprimaria y secundarias (clock skew, NTP)
  - Ausencia de plan de recuperación ante fallo del datacenter primario: tiempo de promoción, validación de estado
  - No menciona persistencia de eventos (durabilidad de Kafka) ni garantías de entrega (at-least-once vs exactly-once) para auditoría de billing

- **Respuesta mejorada sugerida:**

  > Diseñaría una **arquitectura híbrida estratificada** con criterios claros de elección:

**Topología de Comunicación:**
- **Síncrono (gRPC con protobuf):** Autenticación, autorización, billing. Timeout adaptativo por región (800ms US-EU, 1200ms intercontinental). Circuit breaker con fallback a cache si primaria cae.
- **Asíncrono (Kafka):** Reproducción, métricas, eventos de auditoría. Partición por tenant-region para paralelismo y aislamiento. Garantía exactly-once para eventos de billing mediante idempotency keys + deduplicación.

**Resiliencia Multinivel:**
1. **Bulkheads granulares:** Por tenant, servicio y ruta crítica. Límite máximo de conexiones/threads por tenant, CPU cores reservados para operaciones billing.
2. **Circuit breaker adaptativo:** Threshold dinámico basado en p99 latency histórica por región. Reset gradual (half-open).
3. **Retry con backoff exponencial jittered:** Solo en operaciones idempotentes. Para billing, usar patrón Saga coreografía con compensación (rollback).
4. **Rate limiting distribuido:** Token bucket con Redis distribuido. Límites por tier de usuario.
5. **Timeout escalonado:** Auth 200ms, billing 1500ms, lectura de metadatos 3000ms. Cancelación por context timeout.

**Consistencia Multi-región:**
- **Arquitectura primaria-secundaria con quorum de lectura:** Primaria (us-east-1) escribe sesiones en base de datos con replicación física a secundarias (eu-west-1, ap-southeast-1). Lecturas pueden servirse desde réplicas si lag < 500ms, degradan a última versión stale certificada si excede.
- **Event Sourcing + CQRS para sesiones:** Log de eventos inmutable en primaria (Kafka), proyecciones sincronizadas a cada región. Snapshot cada 1000 eventos.
- **Consenso raft distribuido (etcd):** Metadata crítico (configuración, state machine de sesión). Leader election automática en fallo de primaria.
- **Billing: escribir y leer desde primaria sincronizadamente.** Replicación asíncrona a secundarias solo post-confirmación. Transacciones distribuidas con patrón Saga para consistencia eventual controlada.
- **Cache local (Redis cluster) por región con TTL 5min + invalidación basada en eventos,** versión tagged. Degradación inteligente: si replica cae, sirve versión anterior conocida como 'stale_ok'.

**Observabilidad y Detección de Cascadas:**
- **Distributed tracing extremo:** Jaeger con sampler adaptativo (100% en errores, 1% en éxito). Logs estructurados (JSON) con correlation ID, trace ID, span ID, tenant ID, región.
- **Métricas por servicio-endpoint-región:** Prometheus con cardinal controlada. Dashboards por SLO: latencia p50/p99/p999, error rate, apdex score.
- **Alertas en cascada:** Monitoreo de fanout (si un endpoint genera > 10 llamadas downstream), queue depth de Kafka (si > 100k eventos sin procesar), circuit breaker open count.
- **Heartbeats y liveness checks:** Entre servicios cada 10s. GraphQL query para health de dependencias.
- **Análisis de correlación:** Si latency p99 sube en región A, correlacionar con error rates en dependencias upstream/downstream.

**Trade-offs Explícitos:**
- Timeout agresivo vs false positive: compensado con retry exponencial y bulkheads.
- Eventual consistency vs fuerte: crítico para billing, flexible para sesiones.
- Complejidad operacional de multi-región vs disponibilidad global: RTO 5min, RPO 1min para billing.
- Cache TTL vs actualización en tiempo real: 5min con invalidación por evento es compromiso válido para video streaming.

## Resultado general (RF-06)

- **Nivel estimado:** intermedio
- **Puntaje general (IA):** 75/100
- **Promedio calculado (ancla local):** 75.0/100
- **Áreas fuertes:**
  - Comprensión sólida del teorema CAP y su aplicación práctica en decisiones de diseño
  - Capacidad de proponer arquitecturas híbridas que balancean sincronía y asincronía según criticidad
  - Dominio de patrones de resiliencia modernos (circuit breaker, retry exponencial, bulkheads, caché inteligente)
  - Identificación correcta de diferenciación de consistencia por dominio (fuerte en pagos, eventual en datos no-críticos)
  - Stack de observabilidad coherente (trazas distribuidas, métricas, correlation IDs)
  - Pensamiento sobre idempotencia y no-duplicación en sistemas distribuidos
  - Capacidad de estructurar flujos de eventos asíncronos con justificación clara

- **Áreas de mejora:**
  - Falta de especificidad técnica en soluciones: ausencia de algoritmos concretos (Raft, Paxos, quorum) para consenso distribuido y resolución de conflictos geográficos
  - Inconsistencia en parámetros de configuración: timeouts (500ms) y TTLs (30s) demasiado agresivos sin análisis de latencia real en WAN intercontinental
  - Omisión de patrones transaccionales distribuidos: no menciona Sagas, compensating transactions ni garantías de entrega (at-least-once vs exactly-once) en contextos críticos
  - Falta de análisis explícito de trade-offs: no cuantifica impacto de decisiones en SLA, latency budgets ni ventanas de inconsistencia
  - Débil cobertura de state management distribuido: no especifica tecnologías concretas (Redis, Consul, etcd) ni estrategias de replicación (master-slave vs multi-master)
  - Ausencia de estrategias de mitigación de cascadas en detail: dead letter queues, backpressure, rate limiting distribuido, canary deployments
  - No aborda escenarios de fallo crítico: split-brain entre datacenters, clock skew, promoción de réplicas secundarias, validación de estado post-fallo
  - Falta de consideración operacional: monitoring activo de síntomas (profundidad de colas, fanout), SLAs diferenciados por región, priorización de tráfico en degradación


## Plan de mejora personalizado (RF-07)

- Paso 1: Profundizar en algoritmos de consenso distribuido (Raft, Paxos, Byzantine Fault Tolerance) y practicar análisis de quórum para resolución de conflictos geográficos; estudiar casos reales en etcd, Consul, CockroachDB
- Paso 2: Dominar patrones de transacciones distribuidas: estudiar Sagas orquestadas vs coreografía, transacciones compensatorias, garantías de entrega (at-least-once, exactly-once, idempotencia) con ejemplos en Kafka y bases de datos
- Paso 3: Realizar análisis cuantitativo de latency budgets: desglosar presupuesto end-to-end en hops de red, procesamiento, I/O; validar timeouts y TTLs contra latencia real de WAN intercontinental (estudiar latency profiles globales)
- Paso 4: Estudiar CQRS y Event Sourcing en profundidad: immutabilidad, snapshots, log distribuido consistente, proyecciones por región; practicar con arquitecturas de streaming (Kafka Streams, Apache Flink)
- Paso 5: Investigar state management distribuido con hands-on: Redis Sentinel para sesiones, Consul para metadata, etcd para configuración; validar replicación, failover automático y resolución de split-brain
- Paso 6: Documentar estrategias operacionales completas: SLAs diferenciados por servicio y región, priorización de tráfico en degradación, canary deployments, feature flags, rate limiting distribuido con token bucket
- Paso 7: Practicar diseño de observabilidad resiliente: definir alertas en fanout requests, queue depth, clock skew; simular fallos con chaos engineering (network partitions, latency injection, cascades)
- Paso 8: Estudiar recuperación ante desastres: RTO/RPO, promoción de réplicas, validación de estado, backups con durabilidad garantizada; practicar runbooks para escenarios críticos (fallo de datacenter primario)


## Trazabilidad de IA (RF-10 / RNF-05)

Se registraron **5 llamadas** a la IA (prompt exacto, respuesta cruda, modelo, criterios y fecha/hora). Muestra del prompt y respuesta de la primera llamada:

- **Tipo:** pregunta  |  **Modelo:** claude-haiku-4-5  |  **Versión prompt:** 1.0  |  **Fecha:** 2026-07-21T04:11:06.713489+00:00

```
SYSTEM PROMPT: Eres un asistente de práctica para entrevistas técnicas. Tu evaluación es una herramienta de estudio y práctica, NO una certificación oficial ni una garantía de resultado. NUNCA afirmes que la persona aprobará una entrevista real, será contratada, ni des garantías sobre procesos de reclutamiento reales. Respondes SIEMPRE con un único objeto JSON válido, sin texto antes ni después, sin [...]

USER PROMPT: Rol: Arquitecto de Software Tecnología: Sistemas distribuidos Nivel: senior Tipo de entrevista: arquitectura Plantea una pregunta de diseño o arquitectura básica. Redacta la pregunta en español. Aún no se ha realizado ninguna pregunta en esta sesión. Genera ahora la siguiente pregunta como un único objeto JSON.

RESPUESTA CRUDA: ```json { "pregunta": "Estás diseñando una plataforma de comercio electrónico global que debe procesar millones de transacciones diarias con latencia mínima y garantizar consistencia eventual de datos de inventario. ¿Cómo abordarías la tensión entre consistencia fuerte y disponibilidad en este sistema? Describe tu estrategia de particionamiento de datos, sincronización entre regiones geográficas y el patrón de comunicación que utilizarías entre servicios de pago, inventario y [...]
```


**Resumen de todas las trazas de esta entrevista:**

| # | Tipo | Modelo | Versión prompt | Fecha/hora |
|---|------|--------|----------------|------------|
| 1 | pregunta | claude-haiku-4-5 | 1.0 | 2026-07-21T04:11:06.713489+00:00 |
| 2 | evaluacion | claude-haiku-4-5 | 1.0 | 2026-07-21T04:11:23.698468+00:00 |
| 3 | pregunta | claude-haiku-4-5 | 1.0 | 2026-07-21T04:11:27.216451+00:00 |
| 4 | evaluacion | claude-haiku-4-5 | 1.0 | 2026-07-21T04:11:52.946670+00:00 |
| 5 | resumen | claude-haiku-4-5 | 1.0 | 2026-07-21T04:12:03.363755+00:00 |
