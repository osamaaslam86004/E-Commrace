import json

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse

from cart.models import Cart, CartItem
from i.models import Monitors
from tests.books.books_factory_classes import BookAuthorNameFactory, BookFormatFactory
from tests.cart.factory_classes import CartFactory, CartItemFactory
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i.factory_classes import (
    ComputerSubCategoryFactory,
    MonitorsFactory,
    ProductCategoryFactory,
)
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def setup_method():
    """Test setup method to initialize the required data."""

    # Create a user
    user = CustomUserOnlyFactory(user_type="SELLER", password="User1122334455!")
    assert get_user_model().objects.filter(id=user.id).exists()

    # Create a Product category for books
    Product_Category = ProductCategoryFactory(name="COMPUTER")
    assert Product_Category is not None

    # Create a computer category for books
    Computer_SubCategory = ComputerSubCategoryFactory(name="MONITOR")
    assert Computer_SubCategory is not None

    # Create monitor product
    monitor = MonitorsFactory(
        user=user,
        Computer_SubCategory=Computer_SubCategory,
        Product_Category=Product_Category,
    )

    assert Monitors.objects.all().count() == 1

    content_type = ContentType.objects.get_for_model(MonitorsFactory._meta.model)

    # Get the content type and object id of the monitor
    content_type_id = content_type.id
    object_id = monitor.monitor_id

    return user, monitor, content_type_id, object_id


@pytest.fixture
def setup_method_books(setup_method):
    """Test setup method to initialize the required data."""

    user, monitor, content_type_id, object_id = setup_method

    # Create a Product category for books
    product_category = ProductCategoryFactory(name="BOOKS")
    assert product_category is not None

    # Create the bookAuthorName
    book_author_name = BookAuthorNameFactory()
    assert book_author_name is not None

    # create BookFormat instance
    book = BookFormatFactory(
        user=user,
        book_author_name=book_author_name,
        product_category=product_category,
    )
    assert book is not None
    assert book.user == user
    assert book.product_category.name == "BOOKS"

    book_content_type = ContentType.objects.get_for_model(BookFormatFactory._meta.model)

    # Get the content type and object id of the monitor
    book_content_type_id = book_content_type.id
    book_object_id = book.id

    return book_author_name, book, book_content_type_id, book_object_id


@pytest.fixture
def setup_session(client: Client, setup_method):
    """Helper method to set user session, and cart_item cookie"""

    # Log-out user to confirm no session cookie exist
    client.logout()

    user, monitor, content_type_id, object_id = setup_method

    client.force_login(user)
    session = client.session

    # Add user_id to cookie "sessionid"
    session["user_id"] = user.id
    session.save()

    # Update session's cookie
    session_cookie_name = settings.SESSION_COOKIE_NAME
    client.cookies[session_cookie_name] = session.session_key

    return client


@pytest.fixture
def setup_session_already_existing_cart(client: Client, setup_method):
    """Helper method to set user session, and cart_item cookie"""

    user, monitor, content_type_id, object_id = setup_method

    # Log-out user to confirm no session cookie exist
    client.logout()

    client.force_login(user)
    session = client.session
    # Add user_id to cookie "sessionid"
    session["user_id"] = user.id

    # Create cart as an already exisitng cart for user
    cart = CartFactory(user=user, subtotal=100, total=100)

    # create cartitem as an already exisitng CartItems
    cart_item = CartItemFactory(
        cart=cart, content_object=monitor, object_id=object_id, quantity=1
    )

    cart_items = CartItem.objects.filter(cart=cart)
    # Prepare cart items in the desired format [[content_type_id, object_id], ...]
    cart_items_cookie_value = [
        [cart_item.content_type.id, cart_item.object_id] for cart_item in cart_items
    ]

    session["cart_items"] = cart_items_cookie_value
    session.save()

    # Update session's cookie
    session_cookie_name = settings.SESSION_COOKIE_NAME
    client.cookies[session_cookie_name] = session.session_key

    return client


@pytest.fixture
def setup_session_already_existing_cart_with_book_monitor(
    client: Client, setup_method, setup_method_books
):
    """Helper method to set user session, and cart_item cookie"""

    # Log-out user to confirm no session cookie exist
    client.logout()

    # setup monitor product
    user, monitor, content_type_id, object_id = setup_method
    # setup book product
    book_author_name, book, book_content_type_id, book_object_id = setup_method_books

    client.force_login(user)
    session = client.session
    # Add user_id to cookie "sessionid"
    session["user_id"] = user.id

    # Create cart as an already exisitng cart for user
    cart = CartFactory(user=user)

    # create cartitem as an already exisitng CartItems with Monitor
    cart_item_monitor = CartItemFactory(
        cart=cart, content_object=monitor, object_id=object_id, quantity=1
    )
    cart_item_book = CartItemFactory(
        cart=cart, content_object=book, object_id=book_object_id, quantity=1
    )

    cart_items = CartItem.objects.filter(cart=cart)
    # Prepare cart items in the desired format [[content_type_id, object_id], ...]
    cart_items_cookie_value = [
        [cart_item.content_type.id, cart_item.object_id] for cart_item in cart_items
    ]

    session["cart_items"] = cart_items_cookie_value
    session.save()

    # Update session's cookie
    session_cookie_name = settings.SESSION_COOKIE_NAME
    client.cookies[session_cookie_name] = session.session_key

    return client


@pytest.fixture
def setup_session_already_existing_cart_with_quantity_three(
    client: Client, setup_method
):
    """Helper method to set user session, and cart_item cookie"""

    # Log-out user to confirm no session cookie exist
    client.logout()

    user, monitor, content_type_id, object_id = setup_method

    client.force_login(user)
    session = client.session
    # Add user_id to cookie "sessionid"
    session["user_id"] = user.id

    # Create cart as an already exisitng cart for user
    cart = CartFactory(user=user, subtotal=100, total=100)

    # create cartitem as an already exisitng CartItems
    CartItemFactory(cart=cart, content_object=monitor, object_id=object_id, quantity=3)

    # Prepare cart items in the desired format [[content_type_id, object_id], ...]
    cartitems = CartItem.objects.filter(cart=cart)

    # init cookie value as list
    cart_items_cookie_value = []

    for cartitem in cartitems:
        for quantity in range(cartitem.quantity):
            cart_items_cookie_value.append(
                [cartitem.content_type.id, cartitem.object_id]
            )

    assert len(cart_items_cookie_value) == 3

    session["cart_items"] = cart_items_cookie_value
    session.save()

    # Update session's cookie
    session_cookie_name = settings.SESSION_COOKIE_NAME
    client.cookies[session_cookie_name] = session.session_key

    return client


@pytest.mark.django_db
class Test_add_to_cart:

    def test_add_monitor_to_cart_for_logged_in_user(
        self, setup_session: Client, setup_method
    ):

        user, monitor, content_type_id, object_id = setup_method

        client = setup_session

        # Add the monitor to the cart
        response = client.get(
            reverse("cart:add_to_cart", args=[content_type_id, object_id])
        )

        # Check that the user is redirected to the cart view
        assert response.status_code == 302
        assert response.url == reverse("cart:cart_view")

        # Check that the cart and cart item are created
        cart = Cart.objects.filter(user__id=client.session["user_id"]).first()
        assert cart is not None
        assert CartItem.objects.filter(cart=cart, object_id=monitor.monitor_id).exists()

        # Check if the cart_items session data is updated correctly
        cart_items = client.session.get("cart_items", [])
        assert [content_type_id, object_id] in cart_items

        # Assert that the cart subtotal and total were updated
        assert cart.subtotal == monitor.price
        assert cart.total == monitor.price

    def test_add_to_cart_expired_session(self, client: Client, setup_method):
        """Test redirecting to login when the session has expired."""
        client.logout()

        user, monitor, content_type_id, object_id = setup_method

        response = client.get(
            reverse("cart:add_to_cart", args=[content_type_id, object_id])
        )

        # Check that the user is redirected to the login page
        assert response.status_code == 302
        assert response.url == reverse("Homepage:login")

        # Check if the appropriate message is displayed
        messages = list(get_messages(response.wsgi_request))
        assert any(
            "Your session has expired, please log-in first!" in str(m.message)
            for m in messages
        )

    def test_add_to_cart_existing_item(
        self, setup_method, setup_session_already_existing_cart
    ):
        """Test adding an existing item to the cart and increasing the quantity."""

        user, monitor, content_type_id, object_id = setup_method

        client = setup_session_already_existing_cart

        # get the cart for user
        cart = Cart.objects.get(user=user)

        # Add the same item to the cart again
        response = client.get(
            reverse("cart:add_to_cart", args=[content_type_id, object_id])
        )
        # Check that the user is redirected to the cart view
        assert response.status_code == 302
        assert response.url == reverse("cart:cart_view")

        # Check that the cart item quantity is increased in database
        cart_item = CartItem.objects.get(cart=cart, object_id=monitor.monitor_id)
        assert cart_item.quantity == 2
        # Check that the cart item quantity is increased in cookie
        assert len(client.session["cart_items"]) == 2


@pytest.mark.django_db
class Test_RemoveFromCart:

    def test_remove_cart_item_delete_when_quantity_is_one(
        self, setup_method, setup_session_already_existing_cart: Client
    ):
        """Test reducing quantity of a cart item in the cart"""

        user, monitor, content_type_id, object_id = setup_method

        client = setup_session_already_existing_cart

        # URL for remove from cart
        response = client.get(
            reverse(
                "cart:remove_from_cart",
                kwargs={"content_id": content_type_id, "product_id": object_id},
            )
        )

        # Check that the response is a redirect to the cart view
        assert response.status_code == 302
        assert response.url == reverse("cart:cart_view")

        # Check that the cart item quantity is reduced in the database
        cart = Cart.objects.filter(user=user)
        assert cart.count() == 1
        # cartitem is deleted
        assert not CartItem.objects.filter(cart=cart.first()).exists()

        # Check that the cart item quantity is reduced in the cookie
        assert client.session["cart_items"] == []

    def test_remove_cart_item_reduce_quantity_by_one(
        self,
        setup_method,
        setup_session_already_existing_cart_with_quantity_three: Client,
    ):
        """Test reducing quantity of a cart item in the cart when quantity > 1."""

        user, monitor, content_type_id, object_id = setup_method

        client = setup_session_already_existing_cart_with_quantity_three

        # URL for remove from cart
        response = client.get(
            reverse(
                "cart:remove_from_cart",
                kwargs={"content_id": content_type_id, "product_id": object_id},
            )
        )

        # Check that the response is a redirect to the cart view
        assert response.status_code == 302
        assert response.url == reverse("cart:cart_view")

        cart = Cart.objects.filter(user=user)
        assert cart.count() == 1

        # Check that the cart item quantity is reduced by 1 in the database
        cartitem = CartItem.objects.filter(cart=cart.first())
        assert cartitem.count() == 1
        assert cartitem.first().quantity == 2

        # Check that the cart item quantity is reduced by 1 in the cookie

        assert len(client.session["cart_items"]) == 2

    def test_remove_cart_item_no_session(self, setup_method, client: Client):
        """Test handling removal when there's no session available."""
        user, cart_item, content_type_id, product_id = setup_method

        # URL for remove from cart
        response = client.get(
            reverse(
                "cart:remove_from_cart",
                kwargs={"content_id": content_type_id, "product_id": product_id},
            )
        )

        # Check for invalid request response (no session)
        assert response.status_code == 302
        assert response.url == reverse("cart:cart_view")


@pytest.mark.django_db
class Test_CartView:

    def test_cart_view_with_items(
        self,
        setup_method,
        setup_method_books,
        setup_session_already_existing_cart_with_book_monitor: Client,
    ):
        """Test when the user has items in the cart."""

        client = setup_session_already_existing_cart_with_book_monitor
        response = client.get(reverse("cart:cart_view"))

        # Assertions for status code
        assert response.status_code == 200
        assert response.context["cart_items"] == 2
        assert response.context["sub_total"] > 0
        assert response.context["total_amount"] > response.context["sub_total"]
        assert len(response.context["results"]) == 2

    def test_cart_view_without_items(
        self,
        setup_method,
        setup_session: Client,
    ):
        """Test when the user has no items in the cart."""

        user, monitor, content_type_id, object_id = setup_method

        client = setup_session
        client.logout()

        response = client.get(reverse("cart:cart_view"))

        # Assertions for status code
        assert response.status_code == 200
        assert response.context["results"] is None  # No items in the cart
