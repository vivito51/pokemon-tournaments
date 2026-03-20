from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from app.services.database import get_events
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # luego lo afinamos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    return sqlite3.connect("events.db")


@app.get("/events")
def read_events(
    game: Optional[str] = Query(None),
    types: Optional[str] = Query(None),  # ahora puede ser lista separada por comas
    store: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    type_list = types.split(",") if types else None
    return get_events(game=game, types=type_list, store=store, date_from=date_from, date_to=date_to)

@app.get("/stores")
def get_stores():

    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("SELECT DISTINCT store FROM events ORDER BY store")

    stores = [r[0] for r in rows]

    conn.close()

    return stores

@app.get("/types")
def get_types():

    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("SELECT DISTINCT type FROM events")

    types = [r[0] for r in rows]

    conn.close()

    return types

@app.get("/games")
def get_games():

    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("SELECT DISTINCT game FROM events")

    games = [r[0] for r in rows]

    conn.close()

    return games