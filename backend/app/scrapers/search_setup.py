import random
import time
import logging

from app.core.settings import get_settings

logger = logging.getLogger(__name__)


def human_delay(a=None, b=None):
    settings = get_settings()
    min_delay = settings.scraper_action_delay_min if a is None else a
    max_delay = settings.scraper_action_delay_max if b is None else b
    time.sleep(random.uniform(min_delay, max_delay))


def setup_madrid_search(page):
    logger.info("Setting up Madrid search automatically")

    # aceptar cookies
    try:
        time.sleep(15)
        page.get_by_text("Accept All").click()
        logger.info("Cookies accepted")
        human_delay(1.5, 2.8)
    except Exception:
        pass

    page.locator("input[placeholder='Enter your city']").first.click()
    human_delay(1.2, 2.4)

    page.keyboard.type("Madrid", delay=50)
    human_delay(1.5, 2.6)
    
    # Presionar Enter para seleccionar la opción
    page.keyboard.press("Enter")

    human_delay(1.2, 2.2)

    try:
        page.get_by_role("button", name="Search Locations", exact=True).click()
    except Exception:
        logger.warning("Exact Search Locations button not found, trying fallback selector")
        page.locator("button").filter(has_text="Search Locations").last.click()

    logger.info("Search executed")

    human_delay(4, 7)
