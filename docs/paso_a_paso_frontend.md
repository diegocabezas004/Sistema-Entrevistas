# Paso a paso — Frontend

> Recorrido de la interfaz web y de qué pasa en cada pantalla y clic.
> Sirve para entender el código de la UI y para explicarlo en la defensa.
> Cada paso apunta al archivo real.

El frontend es **server-rendered con Jinja2** — HTML generado en el servidor, sin
React ni JavaScript de framework. Usa el patrón **POST-Redirect-GET**: los
formularios hacen POST, el servidor procesa y redirige (303) a un GET que dibuja
la página. Ventaja: recargar nunca reenvía el formulario, y si la IA falla basta
con recargar para reintentar sin perder el avance.

**Regla clave:** la web **no** tiene lógica de negocio ni habla con la IA ni con
la base de datos. Solo llama al mismo `InterviewService` que usa la API REST, y
después presenta. Es una capa de presentación delgada.

---

## Archivos de la capa web

```
app/web/
  __init__.py            Expone el router.
  routes.py              Las rutas de las 3 pantallas + helpers de presentación.
  templates/
    base.html            Plantilla base (layout, cabecera, aviso legal, estilos).
    _recorrido.html      Parcial reutilizable: el track de progreso de preguntas.
    configurar.html      Pantalla 1.
    entrevista.html      Pantalla 2.
    resultado.html       Pantalla 3.
  static/
    estilos.css          Todos los estilos (sin frameworks CSS).
```

`base.html` es la plantilla madre: define el layout, la cabecera, el pie con el
aviso "herramienta de práctica, no certificación" y enlaza `estilos.css`. Las
otras tres plantillas la extienden.

---

## Mapa de rutas (las 3 pantallas)

| Pantalla | Ruta (GET) | Qué hace |
|---|---|---|
| Configurar | `/ui` | Formulario de config + escenarios demo + historial |
| Responder | `/ui/entrevistas/{id}` | Muestra la pregunta activa y su retroalimentación |
| Resultado | `/ui/entrevistas/{id}/resultado` | Puntaje general, plan y desglose |

La raíz `/` redirige a `/ui`. Todo está en `app/web/routes.py`.

---

## Pantalla 1 — Configurar entrevista (RF-01, RF-08, RF-09)

**Ruta GET:** `/ui` → `configurar()` · **Plantilla:** `configurar.html`

1. El GET carga el **historial** de entrevistas (`service.listar_historial()`) y
   le pone etiquetas legibles (ej: nivel `junior` → "Junior", tipo `tecnica` →
   "Técnica"). Esto cubre RF-08/RF-09 (ver sesiones anteriores y comparar).
2. Pasa a la plantilla las opciones válidas (niveles, tipos, idiomas, rango de
   preguntas), que salen de `app/validation/constants.py` — así el formulario y
   la validación del backend usan la **misma** fuente de verdad.
3. Muestra tres **escenarios de demostración** predefinidos (junior, intermedio,
   arquitectura) — los de la sección 7 del enunciado — listos para la demo en vivo.

**Ruta POST:** `/ui/entrevistas` → `crear()`

4. Al enviar el formulario, llama a `service.iniciar_entrevista(...)`.
5. Si la config es inválida (`ValidationError`), redirige de vuelta a `/ui`
   arrastrando el mensaje de error en el query (`?e=...`) para mostrarlo.
6. Si todo bien, redirige (303) a `/ui/entrevistas/{id}` — la pantalla 2.

---

## Pantalla 2 — Responder preguntas (RF-02, RF-03, RF-04, RF-05)

**Ruta GET:** `/ui/entrevistas/{id}` → `entrevista()` · **Plantilla:** `entrevista.html`

Acá está la parte más interesante: **la llamada costosa a la IA se hace de forma
perezosa en el GET.**

1. Lee el detalle de la entrevista. Si no existe, vuelve a `/ui` con un mensaje.
2. Busca la primera pregunta **sin responder** (la "pendiente").
3. Si **no hay** pregunta pendiente:
   - si ya se generaron todas las configuradas → redirige al **resultado**;
   - si faltan → llama a `service.generar_siguiente_pregunta()` para **generar la
     siguiente pregunta con IA** en ese momento, y la vuelve a leer.
   - Si la IA falla acá, se captura y se muestra el error en la misma página; el
     usuario **recarga** para reintentar (RF-12/RNF-06), sin romper la sesión.
4. Toma la **última evaluación** disponible para mostrar la retroalimentación de
   la pregunta que el usuario acaba de responder, antes de seguir (RF-05).
5. Construye el **recorrido** (`_recorrido()`): una fila por pregunta con su
   estado (activa / evaluada / respondida / abierta / pendiente) y su puntaje.
   Las que aún no se generaron aparecen como "Por generar", para que el usuario
   vea desde el inicio cuántas faltan. Se dibuja con el parcial `_recorrido.html`.
6. Renderiza `entrevista.html`: contexto de la entrevista, el track de progreso,
   la pregunta activa y la última retroalimentación.

**Ruta POST:** `/ui/entrevistas/{id}/preguntas/{pid}/respuesta` → `responder()`

7. Al enviar la respuesta, llama a `service.responder_pregunta(...)`, que la
   guarda y la **evalúa con IA** (RF-03/RF-04).
8. Redirige (303) de vuelta a `/ui/entrevistas/{id}`. En ese GET siguiente se
   muestra la retroalimentación y se genera la próxima pregunta. El ciclo se
   repite hasta agotar las preguntas configuradas.

> Ese ida y vuelta (POST responder → redirect → GET que evalúa/genera) es el
> corazón del flujo de la UI. Todo sin JavaScript.

---

## Pantalla 3 — Resultado y plan de mejora (RF-06, RF-07)

**Ruta GET:** `/ui/entrevistas/{id}/resultado` → `resultado()` · **Plantilla:** `resultado.html`

1. Lee el detalle. Si no existe, vuelve a `/ui`.
2. Si la entrevista **todavía no tiene resumen**, llama a
   `service.finalizar_entrevista()` para **generar el resultado y el plan con IA**
   en ese momento (otra vez, perezoso en el GET). Si ya lo tiene, no lo regenera.
   Si la IA falla, muestra el error y se puede recargar.
3. Arma el desglose pregunta por pregunta con su banda de desempeño.
4. Renderiza `resultado.html`: puntaje general, nivel estimado, áreas fuertes,
   áreas de mejora, plan de estudio y el detalle de cada pregunta.

---

## Helpers de presentación (en `routes.py`)

La web tiene funciones de apoyo puramente cosméticas (no tocan negocio):

- **`ETIQUETA_TIPO / ETIQUETA_NIVEL / ETIQUETA_IDIOMA`** — el dominio guarda
  valores canónicos sin tildes (`tecnica`); la UI muestra español correcto
  (`Técnica`).
- **`_banda(puntaje)`** — traduce un puntaje 0–100 a una etiqueta de lectura
  rápida (Sólido / Aceptable / En desarrollo / Inicial). El número exacto siempre
  se muestra al lado, no se esconde.
- **`_recorrido(detalle)`** — construye el track de progreso de preguntas.
- **`_contexto(detalle)`** — empaqueta la config de la entrevista con etiquetas.
- **`_volver(destino, error)`** — hace el redirect 303 arrastrando el error.
- **`_mensaje_de_error(exc)`** — traduce una excepción de dominio a un mensaje
  claro para la pantalla (RNF-06).

---

## Manejo de errores en la UI (RF-12 / RNF-06)

- Los errores se pasan entre páginas por query string (`?e=<mensaje>`), no se
  pierden en el redirect.
- Un fallo de IA nunca deja la sesión rota: como la generación/evaluación ocurre
  en el GET, **recargar la página reintenta** el paso que falló.
- `_mensaje_de_error()` da mensajes distintos según el tipo: config inválida,
  servicio de IA no configurado (falta API key), o IA sin respuesta utilizable.

---

## Por qué se diseñó así (para la defensa)

- **Jinja2 en vez de React:** reduce superficie de trabajo, no necesita build ni
  JS, y encaja con un backend Python. La rúbrica lo permite explícitamente.
- **POST-Redirect-GET:** evita reenvíos de formulario al recargar y hace que el
  reintento ante fallo de IA sea simplemente recargar.
- **IA perezosa en el GET:** el estado siempre queda consistente en la BD; si una
  llamada a IA falla, no hay que rehacer todo, solo recargar.
- **Cero lógica de negocio en la web:** la UI y la API comparten `InterviewService`,
  así no se duplica nada y ambas se comportan igual.

---

## Cómo verlo funcionando

```bash
source venv/bin/activate
python -m app.main            # o: uvicorn app.api.app:app --reload
# abrir http://127.0.0.1:8000/  (redirige a /ui)
```

Pruebas de la web:

```bash
pytest tests/test_web.py -v   # 13 pruebas del flujo completo de la UI
```
