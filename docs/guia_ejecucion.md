# Guía de Ejecución

Pasos para instalar, configurar y ejecutar el sistema desde cero.

## 1. Requisitos previos

- **Python 3.10 o superior** (probado en 3.13).
- Una **API key de Anthropic** (para llamadas reales). Obtenla en <https://console.anthropic.com/>.
  - Las pruebas automatizadas **no** requieren API key.

Verifica tu versión de Python:

```bash
python3 --version
```

## 2. Obtener el proyecto

Sitúate en la carpeta del proyecto (donde está este repositorio):

```bash
cd ProyectoFin/Produccion
```

## 3. Crear y activar el entorno virtual

```bash
python3 -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

## 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 5. Configurar variables de entorno

Copia la plantilla y edítala con tus valores:

```bash
cp .env.example .env
```

Abre `.env` y coloca tu clave real:

```
ANTHROPIC_API_KEY=sk-ant-tu-clave-aqui
ANTHROPIC_MODEL=claude-haiku-4-5
DATABASE_URL=sqlite:///./entrevistas.db
```

> 🔒 **Seguridad:** `.env` está en `.gitignore` y **nunca** debe subirse al repositorio. La API key solo se lee del entorno; jamás está en el código.

## 6. Ejecutar el servidor

```bash
python -m app.main
```

O con recarga automática durante el desarrollo:

```bash
uvicorn app.api.app:app --reload
```

El servidor arranca en `http://127.0.0.1:8000` (configurable con `APP_HOST`/`APP_PORT`).

## 7. Probar que funciona

- **Interfaz web (recomendado para la demo):** abre <http://127.0.0.1:8000/> en el navegador. Son tres pantallas: configurar → responder → resultado. La pantalla inicial incluye tres escenarios de demostración listos para un clic.
- **Documentación interactiva (Swagger):** abre <http://127.0.0.1:8000/docs> en el navegador.
- **Health check:**

  ```bash
  curl http://127.0.0.1:8000/health
  ```

- **Iniciar una entrevista:**

  ```bash
  curl -X POST http://127.0.0.1:8000/entrevistas \
    -H "Content-Type: application/json" \
    -d '{"rol":"Backend Developer","tecnologia":"Python","nivel":"junior","idioma":"es","cantidad_preguntas":3,"tipo":"conceptual"}'
  ```

## 8. Ejecutar las pruebas

```bash
pytest -q
```

Las 80 pruebas corren sin API key (usan motores simulados) y una base SQLite temporal.

## 9. La base de datos

- Se crea automáticamente al iniciar (archivo `entrevistas.db` por defecto).
- Es un archivo SQLite local; puede inspeccionarse con cualquier cliente SQLite.
- Está en `.gitignore`; no se versiona.

## 10. Problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `command not found: python` | El comando es `python3` o el venv no está activado. | Activa el venv o usa `python3`. |
| HTTP 503 al generar/evaluar | Falta `ANTHROPIC_API_KEY`. | Configúrala en `.env`. |
| HTTP 502 al generar/evaluar | La IA falló o no devolvió JSON válido. | Reintenta; revisa conectividad y saldo de la cuenta. |
| `ModuleNotFoundError: anthropic` | Dependencias no instaladas o venv inactivo. | Activa el venv y reinstala `requirements.txt`. |
