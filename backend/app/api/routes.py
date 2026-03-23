from __future__ import annotations

import sqlite3
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.database import get_connection, get_events

router = APIRouter()


def fetch_events(
    game: Optional[str] = None,
    types: Optional[str] = None,
    store: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    type_list = types.split(",") if types else None
    return get_events(
        game=game,
        types=type_list,
        store=store,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/health")
def health_check():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    return {"status": "ok"}


@router.get("/events")
def read_events(
    game: Optional[str] = Query(None),
    types: Optional[str] = Query(None),
    store: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    try:
        return fetch_events(
            game=game,
            types=types,
            store=store,
            date_from=date_from,
            date_to=date_to,
        )
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Could not fetch events") from exc


@router.get("/stores")
def read_stores():
    try:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT store FROM events WHERE store IS NOT NULL ORDER BY store"
            ).fetchall()
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Could not fetch stores") from exc

    return [row[0] for row in rows]


@router.get("/types")
def read_types():
    try:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT type FROM events WHERE type IS NOT NULL ORDER BY type"
            ).fetchall()
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Could not fetch event types") from exc

    return [row[0] for row in rows]


@router.get("/games")
def read_games():
    try:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT game FROM events WHERE game IS NOT NULL ORDER BY game"
            ).fetchall()
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Could not fetch games") from exc

    return [row[0] for row in rows]
