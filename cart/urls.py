from django.urls import path
from cart import views

urlpatterns = [
    # add item to cart
    path(
        "add_to_cart/<int:content_id>/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart",
    ),
    # cart view
    path(
        "cart_view/",
        views.cart_view,
        name="cart_view",
    ),
    # remove item from cart
    path(
        "remove_from_cart/remove/<int:content_id>/<int:product_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
]
