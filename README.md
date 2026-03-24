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

## Despliegue recomendado v1 gratis

### Frontend en Vercel

Segun la documentacion oficial de Vercel para monorepos, debes importar el repositorio y elegir `frontend/` como **Root Directory** del proyecto en Vercel:

- Vercel monorepos: https://vercel.com/docs/monorepos
- Next.js en Vercel: https://vercel.com/docs/frameworks/nextjs

Variable recomendada:

- `NEXT_PUBLIC_API_BASE_URL=`

Con `NEXT_PUBLIC_API_BASE_URL` vacia, el frontend usa `frontend/public/data/events_clean.json`, que sera actualizado automaticamente por GitHub Actions.

### Actualizacion automatica gratis con GitHub Actions

El workflow `.github/workflows/daily-scrape.yml` ejecuta el scraper una vez al dia a las 08:00 de Madrid.

La programacion real se hace con dos horarios UTC y una comprobacion interna de `Europe/Madrid` para respetar el cambio de hora.

Flujo:

1. GitHub Actions ejecuta Playwright.
2. El scraper actualiza `backend/data/` y `frontend/public/data/events_clean.json`.
3. El workflow hace commit y push de los datos nuevos.
4. Vercel redespliega automaticamente la web con los datos actualizados.

## Flujo operativo de v1 gratis

1. GitHub Actions ejecuta el scraper.
2. El scraper escribe JSON, SQLite e ICS.
3. El scraper publica `frontend/public/data/events_clean.json`.
4. El workflow sube esos cambios al repo.
5. Vercel publica automaticamente la nueva version del frontend.
