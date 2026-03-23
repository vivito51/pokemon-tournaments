# Pokemon Madrid Events

Calendario publico de eventos oficiales de Pokemon en Madrid.

## Estructura

- `frontend/`: app Next.js para la web publica.
- `backend/`: API FastAPI, SQLite y scraper con Playwright.

## Arranque local

### 1. Backend

```bash
cd backend
cp .env.example .env
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python run_api.py
```

API local por defecto:

- `http://127.0.0.1:8000`
- healthcheck: `http://127.0.0.1:8000/health`

### 2. Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Frontend local por defecto:

- `http://localhost:3000`

### 3. Refrescar datos

El scraping no se ejecuta al servir usuarios. Se lanza aparte:

```bash
cd backend
. venv/bin/activate
python scrapper_runner.py
```

## Atajos con Makefile

Desde la raiz del repo:

```bash
make backend-dev
make backend-scrape
make frontend-dev
```

## Despliegue recomendado v1

### Frontend en Vercel

Segun la documentacion oficial de Vercel para monorepos, debes importar el repositorio y elegir `frontend/` como **Root Directory** del proyecto en Vercel:

- Vercel monorepos: https://vercel.com/docs/monorepos
- Next.js en Vercel: https://vercel.com/docs/frameworks/nextjs

Variable necesaria:

- `NEXT_PUBLIC_API_BASE_URL=https://TU-BACKEND`

### Backend en Render

Segun la guia oficial de Render para FastAPI, el despliegue base usa:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Fuentes oficiales:

- FastAPI en Render: https://render.com/docs/deploy-fastapi
- Web services: https://render.com/docs/web-services
- Persistent disks: https://render.com/docs/disks

Configuracion recomendada en Render:

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- Environment variables:
  - `CORS_ORIGINS=https://TU-FRONTEND.vercel.app`
  - `FRONTEND_URL=https://TU-FRONTEND.vercel.app`
  - `DB_PATH=/opt/render/project/src/data/events.db`
  - `DATA_DIR=/opt/render/project/src/data`
  - `RAW_EVENTS_PATH=/opt/render/project/src/data/events_raw.json`
  - `CLEAN_EVENTS_PATH=/opt/render/project/src/data/events_clean.json`
  - `CALENDAR_PATH=/opt/render/project/src/data/pokemon_madrid.ics`
  - `SCRAPER_HEADLESS=false`

### Nota importante sobre SQLite

Render indica en su documentacion que el filesystem es efimero por defecto y que para persistir archivos necesitas un **persistent disk** o un datastore externo:

- https://render.com/docs/deploys
- https://render.com/docs/disks

Si mantienes SQLite en esta v1, debes montar un disco persistente y apuntar `DB_PATH` y `DATA_DIR` a esa ruta persistente.

## Flujo operativo de v1

1. Ejecutar scraper manualmente o cuando toque actualizar datos.
2. El scraper escribe JSON, SQLite e ICS.
3. La API FastAPI solo lee esos datos ya generados.
4. El frontend consume la API via `NEXT_PUBLIC_API_BASE_URL`.
