def get_events_for_store(page, store_name):

    print(f"Opening store page for {store_name}")

    events = []

    try:

        with page.expect_response(
            lambda r: "DataActionGetEventsByGUID" in r.url
        ) as resp:

            page.locator(f"text={store_name}").first.click()

        response = resp.value
        data = response.json()

        event_list = data["data"]["Result"]["List"]

        print("Events detected:", len(event_list))

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

        print("Error parsing events:", err)
        print(data)

    # volver atrás
    try:

        page.get_by_text("Back to previous screen").click()

        page.wait_for_selector("text=Search")

        page.wait_for_timeout(1500)

    except Exception as err:

        print("Back button failed:", err)

    return events