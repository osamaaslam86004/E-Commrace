import json
from decimal import Decimal  # Import Decimal module
from django.db.models.fields.files import ImageFieldFile  # Import ImageFieldFile
from cart.models import CartItem
from checkout.models import Payment


MAX_HISTORY_ITEMS = 7  # Maximum number of items to store in the browsing history
MAX_COOKIE_SIZE = 4000  # Maximum size of the cookie data in bytes (4KB)


def add_product_to_cart_history(request, cart_items_in_cookie):
    # Fetch existing browsing history from the session or initialize an empty dictionary
    items_in_cart = request.session.get("cart_items", [])

    # Add details of the new product to the browsing history lists
    items_in_cart.append(cart_items_in_cookie)

    # Ensure all lists in browsing history don't exceed the maximum length
    items_in_cart = items_in_cart[-MAX_HISTORY_ITEMS:]

    # Serialize the browsing history to JSON to estimate its size
    cart_json = json.dumps(items_in_cart)

    cookie_size = len(cart_json.encode("utf-8"))

    # Check if the cookie size exceeds the limit
    if cookie_size > MAX_COOKIE_SIZE:

        # Calculate the excess size and trim lists to fit within the size limit
        excess = cookie_size - MAX_COOKIE_SIZE
        excess_history = json.loads(cart_json[:excess].decode("utf-8"))
        items_in_cart = items_in_cart[len(excess_history) :]

    # Update the session with the modified browsing history
    request.session["cart_items"] = items_in_cart
    request.session.modified = True


def your_cart_items(request):
    if "cart_items" in request.session:
        items_in_cart = request.session.get("cart_items")
        return items_in_cart
    else:
        return []


def update_cart_items(request, payment):
    items_to_remove = []

    if payment.payment_status in ["SUCCESSFUL", "PENDING"]:
        cart_items = CartItem.objects.filter(cart=payment.cart)
        print(f"cart items objects: {cart_items}")

        for item in cart_items:
            print(f"displaying individual item in CartItem: {item}")
            items_to_remove.append([item.content_type.id, item.object_id])

        print(f"items to remove: {items_to_remove}")
        print("Outside the for loop")

        try:
            remove_items_from_cart_history(request, items_to_remove)
            print("Control passed to 'remove_items_from_cart_history'")
            return True
        except Exception as e:
            print(f"Displaying exception: {e}")
            return False


def remove_items_from_cart_history(request, items_to_remove):
    updated_items_in_cart = []

    items_in_cart = request.session.get("cart_items", [])
    print(f"Displaying items in cart session before modification: {items_in_cart}")

    for item in items_in_cart:
        # content_type, object_id = item.get("content_type"), item.get("object_id")
        if item not in items_to_remove:
            updated_items_in_cart.append(item)

    print(f"Updated cart items: {updated_items_in_cart}")

    del request.session["cart_items"]
    request.session["cart_items"] = updated_items_in_cart
    request.session.modified = True

    print("Session modified!")
