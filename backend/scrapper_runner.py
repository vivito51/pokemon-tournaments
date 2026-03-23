import json
import logging
import time
from playwright.sync_api import sync_playwright

from app.core.settings import get_settings
from app.scrapers.search_setup import setup_madrid_search
from app.scrapers.store_scraper import register_store_listener, wait_for_store_results
from app.scrapers.event_scraper import get_events_for_store

from app.services.event_processor import deduplicate_events
from app.services.calendar_generator import generate_calendar
from app.services.database import create_tables, insert_event, reset_events

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run():
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    all_events = []

    create_tables()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=settings.scraper_headless,
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

        logger.info("Total stores detected: %s", len(stores))

        for store in stores:
            logger.info("Scraping store %s", store["name"])
            store_events = []
            try:
                store_events = get_events_for_store(page, store["name"])
            except Exception as err:
                logger.exception("Store scraping failed for %s: %s", store["name"], err)

            all_events.extend(store_events)

            time.sleep(2)

        browser.close()

    # guardar raw
    with open(settings.raw_events_path, "w") as f:
        json.dump(all_events, f, indent=4)
    
    logger.info("Raw events saved: %s", len(all_events))

    # limpiar
    clean_events = deduplicate_events(all_events)

    with open(settings.clean_events_path, "w") as f:
        json.dump(clean_events, f, indent=4)

    logger.info("Clean events: %s", len(clean_events))

    logger.info("Refreshing database events...")
    reset_events()
    for e in clean_events:
        insert_event(e)

    logger.info("Events stored in database")

    generate_calendar(clean_events)

    logger.info("Calendar generated at %s", settings.calendar_path)

if __name__ == "__main__":
    run()
