# Backend

## Variables de entorno

Copia `.env.example` y ajusta los valores si hace falta.

Variables principales:

- `HOST` y `PORT`: host y puerto de FastAPI.
- `DB_PATH`: ruta a la base de datos SQLite.
- `DATA_DIR`: carpeta base para los JSON de eventos.
- `RAW_EVENTS_PATH`: salida de eventos sin limpiar.
- `CLEAN_EVENTS_PATH`: salida de eventos deduplicados.
- `CALENDAR_PATH`: ruta del `.ics`.
- `FRONTEND_EVENTS_PATH`: JSON publico que consumira el frontend cuando no use API.
- `CORS_ORIGINS`: lista separada por comas con los orígenes permitidos.
- `FRONTEND_URL`: URL pública del frontend para añadirla a CORS.
- `SCRAPER_HEADLESS`: `false` por defecto para no tocar el flujo Playwright que ya funciona.
- `SCRAPER_ACTION_DELAY_MIN` y `SCRAPER_ACTION_DELAY_MAX`: pausas entre acciones para hacer el scraping mas humano.
- `SCRAPER_STORE_DELAY_SECONDS`: pausa entre tiendas.

## Arranque de la API

Desde `backend/`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Refresco de datos

El scraper sigue siendo un proceso independiente del backend:

```bash
python scrapper_runner.py
```

Ese comando:

1. Ejecuta el scraping con Playwright.
2. Guarda `events_raw.json`.
3. Deduplica y guarda `events_clean.json`.
4. Inserta en SQLite.
5. Genera `pokemon_madrid.ics`.
6. Publica `frontend/public/data/events_clean.json` para el frontend estatico.

## Healthcheck

La API expone:

```bash
GET /health
```

Devuelve `{"status":"ok"}` si la base de datos está disponible.
