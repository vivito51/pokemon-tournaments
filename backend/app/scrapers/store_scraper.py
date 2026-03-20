from playwright.sync_api import Page

def register_store_listener(page):

    stores = []
    seen_guids = set()

    def handle_response(response):

        if "DataActionGetLocations" in response.url:

            data = response.json()

            locations = data["data"]["Locations"]["List"]

            # print("Stores found:", len(locations))

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
    # esperar a que la lista aparezca
    page.wait_for_selector("text=Search")

    page.wait_for_timeout(3000)