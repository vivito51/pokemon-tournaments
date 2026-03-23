import random
import time
import logging

logger = logging.getLogger(__name__)


def human_delay(a=0.4, b=1.2):
    time.sleep(random.uniform(a, b))


def setup_madrid_search(page):
    logger.info("Setting up Madrid search automatically")

    # aceptar cookies
    try:
        time.sleep(15)
        page.get_by_text("Accept All").click()
        logger.info("Cookies accepted")
        human_delay()
    except Exception:
        pass

    page.locator("input[placeholder='Enter your city']").first.click()
    human_delay()

    page.keyboard.type("Madrid", delay=50)
    human_delay()
    
    # Presionar Enter para seleccionar la opción
    page.keyboard.press("Enter")

    human_delay()

    page.get_by_text("Search Locations").click()

    logger.info("Search executed")

    human_delay(3, 5)
