import logging
import random
import time

from app.core.settings import get_settings

logger = logging.getLogger(__name__)


def human_delay(a=None, b=None):
    settings = get_settings()
    min_delay = settings.scraper_action_delay_min if a is None else a
    max_delay = settings.scraper_action_delay_max if b is None else b
    time.sleep(
        random.uniform(min_delay, max_delay) + settings.scraper_interaction_extra_delay_seconds
    )


def accept_cookies(page):
    try:
        time.sleep(15)
        page.get_by_text("Accept All").click()
        logger.info("Cookies accepted")
        human_delay(1.5, 2.8)
    except Exception:
        pass


def set_search_radius(page, radius_label="50 mi"):
    try:
        logger.info("Expanding search radius to %s", radius_label)
        distance_select = page.locator("select.distance-dropdown").first
        distance_select.wait_for(state="visible", timeout=10000)
        distance_select.select_option(label=radius_label)
        human_delay(1.2, 2.1)
        logger.info("Search radius set to %s", radius_label)
    except Exception as err:
        logger.warning("Could not change search radius to %s: %s", radius_label, err)


def search_city(page, city="Madrid"):
    page.locator("input[placeholder='Enter your city']").first.click()
    human_delay(1.2, 2.4)

    page.keyboard.type(city, delay=50)
    human_delay(1.5, 2.6)

    # Primer Enter: seleccionar la opción de ciudad sugerida
    page.keyboard.press("Enter")
    human_delay(1.2, 2.2)

    # Segundo Enter: ejecutar la búsqueda en la interfaz nueva
    page.keyboard.press("Enter")

    logger.info("Search executed for city %s", city)

    human_delay(4, 7)


def enable_event_list_view(page):
    logger.info("Switching results from locations to events")
    event_toggle = page.locator("input#b3-b2-DoubleSwitch").first
    event_toggle.wait_for(state="visible", timeout=10000)

    try:
        initial_state = event_toggle.is_checked()
        event_toggle.click(force=True)
        page.wait_for_function(
            """
            ({ selector, expectedState }) => {
                const element = document.querySelector(selector);
                return element && element.checked !== expectedState;
            }
            """,
            arg={
                "selector": "input#b3-b2-DoubleSwitch",
                "expectedState": initial_state,
            },
            timeout=10000,
        )
        human_delay(1.2, 2.2)
        logger.info("Event list view enabled")
    except Exception as err:
        logger.warning("Could not switch to event list view: %s", err)
        raise


def setup_madrid_search(page):
    logger.info("Setting up Madrid search automatically")

    accept_cookies(page)
    set_search_radius(page, "50 mi")
    search_city(page, "Madrid")
