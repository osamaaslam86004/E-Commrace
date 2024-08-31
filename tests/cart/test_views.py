# tests/test_views.py
import pytest
from django.urls import reverse
from django.contrib.messages import get_messages

# from django.test import Client
from django.contrib import messages
import random
from django.contrib.contenttypes.models import ContentType
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i.factory_classes import (
    ProductCategoryFactory,
    ComputerSubCategoryFactory,
    MonitorsFactory,
)
from i.models import Special_Features
from Homepage.models import CustomUser
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from cart.models import Cart, CartItem


# @pytest.fixture
# def client():
#     return Client()


@pytest.fixture
def create_product():
    def _create_product(user_type, product_category_name, computer_sub_category_name):
        user = CustomUserOnlyFactory(user_type=user_type)

        # creating the product category
        product_category = ProductCategoryFactory(name=product_category_name)
        # creating the computer sub category
        computer_sub_category = ComputerSubCategoryFactory(
            product_category=product_category, name=computer_sub_category_name
        )
        return user, product_category, computer_sub_category

    return _create_product


@pytest.fixture
def sample_special_feature():
    feature_names = random.sample(
        [choice[0] for choice in Special_Features.SPECIAL_FEATURES_CHOICES], 2
    )
    features = [Special_Features.objects.create(name=name) for name in feature_names]
    return feature_names, features


@pytest.fixture
def build_setup_testing_Review(create_product, sample_special_feature):

    def _build_setup_testing_Review(user_type, product_category, computer_sub_category):
        # build setup for category and user
        user, product_category, computer_sub_category = create_product(
            user_type, product_category, computer_sub_category
        )
        # create the special features
        feature_names, features = sample_special_feature
        # Create the Monitor
        monitor = MonitorsFactory(
            user=user,
            special_features=features,
            Product_Category=product_category,
            Computer_SubCategory=computer_sub_category,
        )
        return user, product_category, computer_sub_category, monitor

    return _build_setup_testing_Review


@pytest.mark.django_db
def test_add_to_cart_anonymous_user(client, build_setup_testing_Review):
    user, product_category, computer_sub_category, monitor = build_setup_testing_Review(
        "SELLER", "COMPUTER", "MONITOR"
    )

    # delete the user to make it anonymous
    user_id = user.id
    user.delete()
    assert not CustomUser.objects.filter(id=user_id).exists()

    # Call the add_to_cart view without logging in
    response = client.get(
        reverse(
            "cart:add_to_cart",
            args=[ContentType.objects.get_for_model(monitor).id, monitor.monitor_id],
        )
    )

    assert response.status_code == 302
    assert response.url == reverse("Homepage:login")

    # Check if the message is correct
    storage = messages.get_messages(response.wsgi_request)
    assert any(
        message.message == "Your session has expired, please log-in first!"
        for message in storage
    )


@pytest.mark.django_db
def test_add_to_cart_view_with_expired_session(client, build_setup_testing_Review):
    user, product_category, computer_sub_category, monitor = build_setup_testing_Review(
        "SELLER", "COMPUTER", "MONITOR"
    )

    # Call the add_to_cart view without logging in
    response = client.get(
        reverse(
            "cart:add_to_cart",
            args=[ContentType.objects.get_for_model(monitor).id, monitor.monitor_id],
        )
    )

    # Check if the view redirects to the login page with a message
    assert response.status_code == 302
    assert response.url == reverse("Homepage:login")
    messages = list(get_messages(response.wsgi_request))
    assert any(
        "Your session has expired, please log-in first!" in str(message)
        for message in messages
    )

    # Check if no cart item was created
    assert not CartItem.objects.exists()

    # Check if no cart was created
    assert not Cart.objects.exists()


@pytest.mark.django_db
def test_add_to_cart_view_with_valid_user(client, build_setup_testing_Review):
    user, product_category, computer_sub_category, monitor = build_setup_testing_Review(
        "SELLER", "COMPUTER", "MONITOR"
    )

    # Log in the user
    client.force_login(user)
    session = client.session
    session["user_id"] = user.id
    session.save()

    assert "user_id" in session and session["user_id"] == user.id

    # Call the add_to_cart view
    response = client.get(
        reverse(
            "cart:add_to_cart",
            args=[ContentType.objects.get_for_model(monitor).id, monitor.monitor_id],
        )
    )

    # Check if the view redirects to the cart view
    assert response.status_code == 302
    assert response.url == reverse("cart:cart_view")

    # Check if the cart item was created
    assert CartItem.objects.filter(
        content_type=ContentType.objects.get_for_model(monitor),
        object_id=monitor.monitor_id,
    ).exists()

    # Check if the cart subtotal and total were updated
    cart = Cart.objects.get(user=user)
    assert cart.subtotal == monitor.price
    assert cart.total == monitor.price


@pytest.mark.django_db
def test_add_to_cart_view_with_existing_cart_item(
    client, user_factory, monitors_factory
):
    # Create a user
    user = user_factory.create()

    # Create a monitor
    monitor = monitors_factory.create()

    # Create a cart with an existing cart item
    cart = Cart.objects.create(user=user)
    cart_item = CartItem.objects.create(
        cart=cart,
        content_type=ContentType.objects.get_for_model(monitor),
        object_id=monitor.id,
        quantity=1,
        price=monitor.price,
    )

    # Log in the user
    client.force_login(user)

    # Call the add_to_cart view
    response = client.get(
        reverse(
            "cart:add_to_cart",
            args=[ContentType.objects.get_for_model(monitor).id, monitor.id],
        )
    )

    # Check if the view redirects to the cart view
    assert response.status_code == 302
    assert response.url == reverse("cart:cart_view")

    # Check if the cart item quantity was updated
    cart_item.refresh_from_db()
    assert cart_item.quantity == 2

    # Check if the cart subtotal and total were updated
    cart.refresh_from_db()
    assert cart.subtotal == monitor.price * 2
    assert cart.total == monitor.price * 2


@pytest.mark.django_db
def test_add_to_cart_view_with_multiple_content_types(
    client, user_factory, monitors_factory, books_format_factory
):
    # Create a user
    user = user_factory.create()

    # Create a monitor and a book format
    monitor = monitors_factory.create()
    book_format = books_format_factory.create()

    # Log in the user
    client.force_login(user)

    # Call the add_to_cart view for the monitor
    response = client.get(
        reverse(
            "cart:add_to_cart",
            args=[ContentType.objects.get_for_model(monitor).id, monitor.id],
        )
    )

    # Check if the view redirects to the cart view
    assert response.status_code == 302
    assert response.url == reverse("cart:cart_view")

    # Check if the cart item for the monitor was created
    assert CartItem.objects.filter(
        content_type=ContentType.objects.get_for_model(monitor), object_id=monitor.id
    ).exists()

    # Call the add_to_cart view for the book format
    response = client.get(
        reverse(
            "cart:add_to_cart",
            args=[ContentType.objects.get_for_model(book_format).id, book_format.id],
        )
    )

    # Check if the view redirects to the cart view
    assert response.status_code == 302
    assert response.url == reverse("cart:cart_view")

    # Check if the cart item for the book format was created
    assert CartItem.objects.filter(
        content_type=ContentType.objects.get_for_model(book_format),
        object_id=book_format.id,
    ).exists()

    # Check if the cart subtotal and total were updated
    cart = Cart.objects.get(user=user)
    assert cart.subtotal == monitor.price + book_format.price
    assert cart.total == monitor.price + book_format.price
