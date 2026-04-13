import logging

from app.core.settings import get_settings

logger = logging.getLogger(__name__)


def interaction_wait(page, milliseconds):
    extra_ms = int(get_settings().scraper_interaction_extra_delay_seconds * 1000)
    page.wait_for_timeout(milliseconds + extra_ms)


def wait_for_store_results_ready(page):
    page.wait_for_selector("input[placeholder='Enter your city']", timeout=15000)
    interaction_wait(page, 1800)

    try:
        page.get_by_text("Back to previous screen").wait_for(state="hidden", timeout=10000)
    except Exception:
        logger.debug("Back button still present or hidden wait timed out while preparing results list")


def scroll_store_results(page):
    scrolled = page.evaluate(
        """
        () => {
          const nodes = Array.from(document.querySelectorAll('*'));
          const scrollables = nodes.filter((node) => {
            const style = window.getComputedStyle(node);
            const overflowY = style.overflowY;
            return (
              (overflowY === 'auto' || overflowY === 'scroll') &&
              node.scrollHeight > node.clientHeight + 40
            );
          });

          const target =
            scrollables.find((node) => /Search Locations|Store/i.test(node.innerText || '')) ||
            scrollables[0];

          if (target) {
            target.scrollBy({ top: 1400, behavior: 'auto' });
            return true;
          }

          window.scrollBy(0, 1400);
          return false;
        }
        """
    )

    interaction_wait(page, 900)
    return scrolled


def find_store_locator(page, store_name, max_scroll_attempts=18):
    logger.info("Looking for store in results list: %s", store_name)

    wait_for_store_results_ready(page)

    page.evaluate(
        """
        () => {
          const nodes = Array.from(document.querySelectorAll('*'));
          const scrollables = nodes.filter((node) => {
            const style = window.getComputedStyle(node);
            const overflowY = style.overflowY;
            return (
              (overflowY === 'auto' || overflowY === 'scroll') &&
              node.scrollHeight > node.clientHeight + 40
            );
          });

          const target =
            scrollables.find((node) => /Search Locations|Store/i.test(node.innerText || '')) ||
            scrollables[0];

          if (target) {
            target.scrollTo({ top: 0, behavior: 'auto' });
          } else {
            window.scrollTo(0, 0);
          }
        }
        """
    )
    interaction_wait(page, 800)

    locator = page.get_by_text(store_name, exact=True).first

    for attempt in range(max_scroll_attempts):
        try:
            if locator.count() > 0:
                locator.scroll_into_view_if_needed(timeout=3000)
                interaction_wait(page, 400)
                return locator
        except Exception:
            pass

        logger.info(
            "Store %s not visible yet, scrolling results (attempt %s/%s)",
            store_name,
            attempt + 1,
            max_scroll_attempts,
        )
        scroll_store_results(page)

    raise TimeoutError(f"Store result not found in rendered list: {store_name}")


def get_events_for_store(page, store_name):
    logger.info("Opening store page for %s", store_name)

    events = []
    data = None

    try:

        with page.expect_response(
            lambda r: "DataActionGetEventsByGUID" in r.url
        ) as resp:
            store_locator = find_store_locator(page, store_name)
            store_locator.click()

        response = resp.value
        data = response.json()
        interaction_wait(page, 2200)
        page.get_by_text("Back to previous screen").wait_for(state="visible", timeout=10000)

        event_list = data["data"]["Result"]["List"]

        logger.info("Events detected for %s: %s", store_name, len(event_list))

        for event in event_list:

            e = event["Events"]

            events.append({
                "name": e["Name"],
                "date": e["Start_date"],
                "game": e["Products"]["List"][0],
                "type": event["EventTypeName"],
                "store": store_name,
                "address": e["Address"]["Full_address"]
            })

    except Exception as err:
        logger.exception("Error parsing events for %s: %s", store_name, err)
        if data is not None:
            logger.debug("Last response data for %s: %s", store_name, data)

    # volver atrás
    try:
        page.get_by_text("Back to previous screen").click()
        page.get_by_text("Back to previous screen").wait_for(state="hidden", timeout=10000)
        wait_for_store_results_ready(page)
        interaction_wait(page, 2200)

    except Exception as err:
        logger.warning("Back button failed for %s: %s", store_name, err)

    return events
