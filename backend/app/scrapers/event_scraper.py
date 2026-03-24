import logging

logger = logging.getLogger(__name__)


def get_events_for_store(page, store_name):
    logger.info("Opening store page for %s", store_name)

    events = []
    data = None

    try:

        with page.expect_response(
            lambda r: "DataActionGetEventsByGUID" in r.url
        ) as resp:

            page.locator(f"text={store_name}").first.click()

        response = resp.value
        data = response.json()

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

        page.wait_for_selector("text=Search")

        page.wait_for_timeout(2500)

    except Exception as err:
        logger.warning("Back button failed for %s: %s", store_name, err)

    return events
