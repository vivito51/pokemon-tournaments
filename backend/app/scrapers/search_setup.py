import logging
import random
import time

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

    try:
        logger.info("Expanding search radius to 50 mi")
        distance_select = page.locator("select.distance-dropdown").first
        distance_select.wait_for(state="visible", timeout=10000)
        distance_select.select_option(label="50 mi")
        human_delay(1.2, 2.1)
        logger.info("Search radius set to 50 mi")
    except Exception as err:
        logger.warning("Could not change search radius to 50 mi: %s", err)

    page.locator("input[placeholder='Enter your city']").first.click()
    human_delay(1.2, 2.4)

    page.keyboard.type("Madrid", delay=50)
    human_delay(1.5, 2.6)
    
    # Primer Enter: seleccionar la opción de ciudad sugerida
    page.keyboard.press("Enter")
    human_delay(1.2, 2.2)

    # Segundo Enter: ejecutar la búsqueda en la interfaz nueva
    page.keyboard.press("Enter")

    logger.info("Search executed")

    human_delay(4, 7)
