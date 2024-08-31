import json
from decimal import Decimal  # Import Decimal module
from django.db.models.fields.files import ImageFieldFile  # Import ImageFieldFile

MAX_HISTORY_ITEMS = 7  # Maximum number of items to store in the browsing history
MAX_COOKIE_SIZE = 4000  # Maximum size of the cookie data in bytes (4KB)


def add_product_to_browsing_history(request, product_details):
    # Fetch existing browsing history from the session or initialize an empty dictionary
    browsing_history = request.session.get(
        "browsing_history",
        {
            "name": [],
            "price": [],
            "rating": [],
            "image_url": [],
            "path": [],
            "special_features": [],
        },
    )

    # Add details of the new product to the browsing history lists
    for key, value in product_details.items():
        browsing_history[key].append(value)

    # Ensure all lists in browsing history don't exceed the maximum length
    for key in browsing_history:
        browsing_history[key] = browsing_history[key][-MAX_HISTORY_ITEMS:]

    # Serialize the browsing history to JSON to estimate its size
    history_json = json.dumps(browsing_history)

    cookie_size = len(history_json.encode("utf-8"))

    # Check if the cookie size exceeds the limit
    if cookie_size > MAX_COOKIE_SIZE:
        # Calculate the excess size and trim lists to fit within the size limit
        excess = cookie_size - MAX_COOKIE_SIZE
        excess_history = json.loads(history_json[:excess].decode("utf-8"))
        browsing_history = {
            key: value[len(excess_history[key]) :]
            for key, value in browsing_history.items()
        }

    # Update the session with the modified browsing history
    request.session["browsing_history"] = browsing_history
    request.session.modified = True


def your_browsing_history(request):
    zipped = []
    if "browsing_history" in request.session:
        browsing_history = request.session.get("browsing_history")
        names = browsing_history.get("name")
        prices = browsing_history.get("price")
        ratings = browsing_history.get("rating")
        product_urls = browsing_history.get("image_url")
        product_path = browsing_history.get("path")
        special_features = browsing_history.get("special_features")

        zipped = list(
            zip(
                names,
                prices,
                [Decimal(string) for string in ratings],
                product_urls,
                product_path,
                special_features,
            )
        )
    else:
        zipped = None
    return zipped
