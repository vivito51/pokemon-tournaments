import sqlite3

DB_PATH = "events.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_tables():

    conn = get_connection()
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

    conn.commit()
    conn.close()


def insert_event(event):

    conn = get_connection()
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

        conn.commit()

    except sqlite3.IntegrityError:
        pass

    conn.close()

def get_events(game=None, types=None, store=None, date_from=None, date_to=None):
    conn = get_connection()
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

    conn.close()

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