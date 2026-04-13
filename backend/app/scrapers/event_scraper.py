import logging

logger = logging.getLogger(__name__)


def wait_for_store_results_ready(page):
    logger.info("Waiting for store results list to be interactable")

    page.wait_for_selector("input[placeholder='Enter your city']")
    page.wait_for_timeout(1800)

    try:
        page.get_by_text("Back to previous screen").wait_for(state="hidden", timeout=5000)
    except Exception:
        pass


def scroll_store_results(page):
    page.evaluate(
        """
        () => {
          const candidates = Array.from(document.querySelectorAll('*')).filter((element) => {
            const style = window.getComputedStyle(element);
            const canScroll = /(auto|scroll)/.test(style.overflowY);
            return canScroll && element.scrollHeight > element.clientHeight + 80;
          });

          const target =
            candidates.find((element) => element.innerText.includes('Search Locations')) ??
            candidates.find((element) => element.innerText.includes('Store')) ??
            candidates.sort((left, right) => right.clientHeight - left.clientHeight)[0];

          if (target) {
            target.scrollBy(0, 1400);
            return;
          }

          window.scrollBy(0, 1400);
        }
        """
    )


def find_store_locator(page, store_name, max_scroll_attempts=18):
    logger.info("Looking for store in results list: %s", store_name)

    wait_for_store_results_ready(page)

    page.evaluate(
        """
        () => {
          const candidates = Array.from(document.querySelectorAll('*')).filter((element) => {
            const style = window.getComputedStyle(element);
            const canScroll = /(auto|scroll)/.test(style.overflowY);
            return canScroll && element.scrollHeight > element.clientHeight + 80;
          });

          const target =
            candidates.find((element) => element.innerText.includes('Search Locations')) ??
            candidates.find((element) => element.innerText.includes('Store')) ??
            candidates.sort((left, right) => right.clientHeight - left.clientHeight)[0];

          if (target) {
            target.scrollTo(0, 0);
            return;
          }

          window.scrollTo(0, 0);
        }
        """
    )
    page.wait_for_timeout(800)

    locator = page.get_by_text(store_name, exact=True).first

    for attempt in range(max_scroll_attempts):
        try:
            if locator.count() > 0:
                locator.scroll_into_view_if_needed(timeout=3000)
                page.wait_for_timeout(400)
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
        page.wait_for_timeout(900)

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
        page.wait_for_timeout(2200)
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
        page.wait_for_timeout(2200)

    except Exception as err:
        logger.warning("Back button failed for %s: %s", store_name, err)

    return events
