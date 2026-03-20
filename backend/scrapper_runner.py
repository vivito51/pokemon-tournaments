import json
import time
from playwright.sync_api import sync_playwright

from app.scrapers.search_setup import setup_madrid_search
from app.scrapers.store_scraper import register_store_listener, wait_for_store_results
from app.scrapers.event_scraper import get_events_for_store

from app.services.event_processor import deduplicate_events
from app.services.calendar_generator import generate_calendar
from app.services.database import create_tables, insert_event


def run():

    all_events = []

    create_tables()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )

        page = context.new_page()

        page.goto("https://events.pokemon.com/en-us/events")

        # Listen stores
        stores = register_store_listener(page)

        # busqueda
        setup_madrid_search(page)

        wait_for_store_results(page)

        page.wait_for_timeout(5000)

        print("Total stores detected:", len(stores))

        for store in stores:

            events = get_events_for_store(page, store["name"])

            all_events.extend(events)

            time.sleep(2)

        browser.close()

    # guardar raw
    with open("data/events_raw.json", "w") as f:
        json.dump(all_events, f, indent=4)
    
    print("Raw events saved:", len(all_events))

    # limpiar
    clean_events = deduplicate_events(all_events)

    with open("data/events_clean.json", "w") as f:
        json.dump(clean_events, f, indent=4)

    print("Clean events:", len(clean_events))

    print("Storing events in database...")
    # guardar en DB
    for e in clean_events:
        insert_event(e)

    print("Events stored in database")

    # generar calendario
    generate_calendar(clean_events)

    print("Calendar generated")

if __name__ == "__main__":
    run()