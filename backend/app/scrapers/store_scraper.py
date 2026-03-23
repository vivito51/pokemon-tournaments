from playwright.sync_api import Page
import logging

logger = logging.getLogger(__name__)

def register_store_listener(page):

    stores = []
    seen_guids = set()

    def handle_response(response):

        if "DataActionGetLocations" in response.url:

            data = response.json()

            locations = data["data"]["Locations"]["List"]

            for loc in locations:

                guid = loc["Guid"]

                if guid in seen_guids:
                    continue

                seen_guids.add(guid)

                stores.append({
                    "guid": loc["Guid"],
                    "name": loc["Address"]["Name"],
                    "address": loc["Address"]["Full_address"]
                })

            page.remove_listener("response", handle_response)

    page.on("response", handle_response)

    return stores

def wait_for_store_results(page):
    logger.info("Waiting for store results")
    page.wait_for_selector("text=Search")

    page.wait_for_timeout(3000)
