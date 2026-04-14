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
from app.services.frontend_export import export_events_for_frontend

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_browser_context(playwright, settings):
    browser = playwright.chromium.launch(
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

    return browser, context


def open_store_results_page(page, settings):
    page.goto("https://events.pokemon.com/en-us/events")
    setup_madrid_search(page)
    wait_for_store_results(page)
    page.wait_for_timeout(
        5000 + int(settings.scraper_interaction_extra_delay_seconds * 1000)
    )


def recover_store_results(page, settings):
    logger.warning("Recovering scraper state back to store results")
    open_store_results_page(page, settings)
    logger.info("Store results recovered")


def collect_stores(playwright, settings):
    browser, context = create_browser_context(playwright, settings)
    page = context.new_page()
    page.goto("https://events.pokemon.com/en-us/events")
    stores = register_store_listener(page)
    setup_madrid_search(page)
    wait_for_store_results(page)
    page.wait_for_timeout(
        5000 + int(settings.scraper_interaction_extra_delay_seconds * 1000)
    )
    return browser, context, page, stores


def split_store_blocks(stores):
    midpoint = (len(stores) + 1) // 2
    return [stores[:midpoint], stores[midpoint:]]


def scrape_store_block(playwright, settings, stores, block_index):
    if not stores:
        logger.info("Skipping empty store block %s", block_index)
        return []

    browser, context = create_browser_context(playwright, settings)
    page = context.new_page()
    all_events = []

    try:
        open_store_results_page(page, settings)

        logger.info(
            "Processing store block %s/%s with %s stores",
            block_index,
            2,
            len(stores),
        )

        for index, store in enumerate(stores):
            logger.info("Scraping store %s", store["name"])
            store_events = []
            try:
                store_events = get_events_for_store(page, store["name"])
            except Exception as err:
                logger.exception("Store scraping failed for %s: %s", store["name"], err)
                remaining = len(stores) - index - 1
                logger.warning(
                    "Skipping %s after failure and attempting recovery. Remaining stores: %s",
                    store["name"],
                    remaining,
                )
                try:
                    recover_store_results(page, settings)
                except Exception as recovery_err:
                    logger.exception(
                        "Recovery failed after store %s: %s",
                        store["name"],
                        recovery_err,
                    )
                    break

            all_events.extend(store_events)
            time.sleep(settings.scraper_store_delay_seconds)
    finally:
        context.close()
        browser.close()

    return all_events


def run():
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    all_events = []

    create_tables()

    with sync_playwright() as p:
        browser, context, page, stores = collect_stores(p, settings)

        try:
            logger.info("Total stores detected: %s", len(stores))

            store_blocks = split_store_blocks(stores)
            logger.info(
                "Split stores into blocks of %s and %s",
                len(store_blocks[0]),
                len(store_blocks[1]),
            )

            first_block_events = []
            logger.info(
                "Processing store block %s/%s with %s stores",
                1,
                2,
                len(store_blocks[0]),
            )

            for index, store in enumerate(store_blocks[0]):
                logger.info("Scraping store %s", store["name"])
                store_events = []
                try:
                    store_events = get_events_for_store(page, store["name"])
                except Exception as err:
                    logger.exception("Store scraping failed for %s: %s", store["name"], err)
                    remaining = len(store_blocks[0]) - index - 1
                    logger.warning(
                        "Skipping %s after failure and attempting recovery. Remaining stores in block: %s",
                        store["name"],
                        remaining,
                    )
                    try:
                        recover_store_results(page, settings)
                    except Exception as recovery_err:
                        logger.exception(
                            "Recovery failed after store %s in first block: %s",
                            store["name"],
                            recovery_err,
                        )
                        break

                first_block_events.extend(store_events)
                time.sleep(settings.scraper_store_delay_seconds)

            all_events.extend(first_block_events)
        finally:
            context.close()
            browser.close()

        second_block_events = scrape_store_block(p, settings, store_blocks[1], 2)
        all_events.extend(second_block_events)

    # guardar raw
    with open(settings.raw_events_path, "w") as f:
        json.dump(all_events, f, indent=4)
    
    logger.info("Raw events saved: %s", len(all_events))

    # limpiar
    clean_events = deduplicate_events(all_events)

    with open(settings.clean_events_path, "w") as f:
        json.dump(clean_events, f, indent=4)

    logger.info("Clean events: %s", len(clean_events))

    export_events_for_frontend(clean_events)
    logger.info("Frontend data exported at %s", settings.frontend_events_path)

    logger.info("Refreshing database events...")
    reset_events()
    for e in clean_events:
        insert_event(e)

    logger.info("Events stored in database")

    generate_calendar(clean_events)

    logger.info("Calendar generated at %s", settings.calendar_path)

if __name__ == "__main__":
    run()
