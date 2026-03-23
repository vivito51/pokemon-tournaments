import sqlite3

from app.core.settings import get_settings

settings = get_settings()
DB_PATH = settings.db_path


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables():
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            game TEXT,
            type TEXT,
            store TEXT,
            address TEXT,
            UNIQUE(date, game, type, store)
        )
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_date ON events(date)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_store ON events(store)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_game ON events(game)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_type ON events(type)")


def insert_event(event):
    with get_connection() as conn:
        cur = conn.cursor()

        try:
            cur.execute("""
            INSERT INTO events (name,date,game,type,store,address)
            VALUES (?,?,?,?,?,?)
            """, (
                event["name"],
                event["date"],
                event["game"],
                event["type"],
                event["store"],
                event["address"]
            ))
        except sqlite3.IntegrityError:
            pass


def reset_events():
    with get_connection() as conn:
        conn.execute("DELETE FROM events")

def get_events(game=None, types=None, store=None, date_from=None, date_to=None):
    with get_connection() as conn:
        cur = conn.cursor()

        query = "SELECT name,date,game,type,store,address FROM events WHERE 1=1"
        params = []

        if game:
            query += " AND game=?"
            params.append(game)

        if types:
            query += f" AND type IN ({','.join(['?']*len(types))})"
            params.extend(types)

        if store:
            query += " AND store=?"
            params.append(store)

        if date_from:
            query += " AND date>=?"
            params.append(date_from)

        if date_to:
            query += " AND date<=?"
            params.append(date_to)

        query += " ORDER BY date ASC"

        rows = cur.execute(query, params).fetchall()

    events = []
    for r in rows:
        events.append({
            "name": r[0],
            "date": r[1],
            "game": r[2],
            "type": r[3],
            "store": r[4],
            "address": r[5]
        })

    return events
