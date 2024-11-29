import json
from email import message
from unittest.mock import patch

import pytest
import stripe
from django.conf import settings
from django.contrib.messages import get_messages
from django.test import Client

# from http.cookies import SimpleCookie
from django.urls import reverse

from cart.models import Cart, CartItem
from checkout.models import Payment, Refund
from Homepage.models import UserProfile
from i.models import Monitors
from tests.cart.factory_classes import CartFactory, CartItemFactory
from tests.checkout.factory_classes import PaymentFactory
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i.factory_classes import (
    ComputerSubCategoryFactory,
    MonitorsFactory,
    ProductCategoryFactory,
)


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user():
    custom_user = CustomUserOnlyFactory(user_type="SELLER")
    assert UserProfile.objects.filter(user=custom_user, age=18).exists()

    return custom_user


@pytest.fixture
def user_profile(user: CustomUserOnlyFactory):
    return UserProfile.objects.filter(user__id=user.id, age=18).first()


@pytest.fixture
def cart(user: CustomUserOnlyFactory):
    return CartFactory(user=user, subtotal=100, total=100)


@pytest.fixture
def cart_item_creation_with_monitor(user: CustomUserOnlyFactory, cart: CartFactory):
    """Test setup method to initialize the required data."""

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
    # create a CartItems item
    cart_items = CartItemFactory(content_object=monitor, cart=cart, quantity=3)

    assert Monitors.objects.all().count() == 1

    # retrieve the monitor
    retrieved_monitor = Monitors.objects.get(user=user)

    assert cart_items.content_object == retrieved_monitor
    assert cart_items.price == retrieved_monitor.price

    return cart_items


@pytest.fixture
def setup_session_without_CartItems(
    client: Client,
    user: CustomUserOnlyFactory,
):
    """Helper method to set user session"""

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
def setup_session_with_quantity_three(
    client: Client,
    user: CustomUserOnlyFactory,
    cart_item_creation_with_monitor: CartItemFactory,
):
    """Helper method to set user session, and cart_item cookie"""

    cart_items = cart_item_creation_with_monitor

    client.force_login(user)
    session = client.session
    # Add user_id to cookie "sessionid"
    session["user_id"] = user.id

    # fetch the cart for logged-in user
    Cart_Items = CartItem.objects.get(id=cart_items.id)

    # Initialize a list
    cart_items_cookie_value = []

    # Prepare cart items in the desired format [[content_type_id, object_id], ...]
    for quantity in range(Cart_Items.quantity):
        cart_items_cookie_value.append(
            [Cart_Items.content_type.id, Cart_Items.object_id]
        )

    assert len(cart_items_cookie_value) == 3

    session["cart_items"] = cart_items_cookie_value
    session.save()

    # Update session's cookie
    session_cookie_name = settings.SESSION_COOKIE_NAME
    client.cookies[session_cookie_name] = session.session_key

    return client


@pytest.mark.django_db
class Test_CheckoutView:

    @pytest.fixture()
    def setup_session(
        self,
        client: Client,
        user: CustomUserOnlyFactory,
        cart_item_creation_with_monitor: CartItemFactory,
    ):
        """Helper method to set user session, and cart_item cookie"""

        self.client = client

        cart_items = cart_item_creation_with_monitor

        self.client.force_login(user)
        session = client.session

        # Add user_id to cookie "sessionid"
        session["user_id"] = user.id

        # init cookie value as list
        cart_items_cookie_value = []

        Cart_Items = CartItem.objects.filter(id=cart_items.id)

        # Prepare cart items in the desired format [[content_type_id, object_id], ...]
        for cartitem in Cart_Items:
            for quantity in range(cartitem.quantity):
                cart_items_cookie_value.append(
                    [cartitem.content_type.id, cartitem.object_id]
                )

        assert len(cart_items_cookie_value) == 3

        session["cart_items"] = json.dumps(cart_items_cookie_value)
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        self.client.cookies[session_cookie_name] = session.session_key

        print(f"{session['cart_items']}")

        return self.client

    def test_get_checkout_view(self, setup_session: Client):
        """Test GET request for checkout page renders correctly."""

        client = setup_session
        response = client.get(reverse("checkout:check_out"))

        assert response.status_code == 200
        assert "stripe_publication_key" in response.context

    @patch("checkout.views.stripe.Customer.search")
    @patch("checkout.views.stripe.Customer.create")
    @patch("checkout.views.stripe.Charge.create")
    def test_post_checkout_payment_success(
        self,
        mock_charge_create,
        mock_customer_create,
        mock_customer_search,
        cart: CartFactory,
        setup_session: Client,
    ):
        """Test POST request to checkout view for successful payment."""
        client = setup_session

        # Mock Stripe customer search to return no existing customer
        mock_customer_search.return_value = {"data": []}

        # Mock Stripe customer create to return no existing customer
        mock_customer_create.return_value = {"id": "test_customer_id"}

        # Mock Stripe charge creation
        mock_charge_create.return_value = {"id": "ch_test_charge_id"}

        # Include sessionid cookie in the POST request to persist session data
        response = client.post(
            reverse("checkout:check_out"), {"stripeToken": "test_stripe_token"}
        )

        # Assertions
        assert response.status_code == 302
        assert response.url == reverse("checkout:check_out")
        payment = Payment.objects.get(cart=cart)
        assert payment.cart.cartitem_set.all().count() == 1
        assert payment.stripe_charge_id == "ch_test_charge_id"

    @patch("checkout.views.stripe.Customer.search")
    @patch("checkout.views.stripe.Charge.create")
    def test_post_checkout_existing_customer(
        self,
        mock_charge_create,
        mock_customer_search,
        cart: CartFactory,
        user_profile: UserProfile | None,
        setup_session: Client,
    ):
        """Test POST request when an existing customer is found."""

        client = setup_session
        # Mock Stripe customer search to return an existing customer
        mock_customer_search.return_value = {
            "data": [
                {
                    "email": user_profile.user.email,
                    "phone": user_profile.phone_number.as_e164,
                    "name": user_profile.full_name,
                    "id": "cus_existing_customer_id",
                    "metadata": {
                        "user_id": str(user_profile.user.id),
                        "cart_id": str(cart.id),
                    },
                }
            ]
        }

        print(mock_customer_search.return_value)

        # Mock Stripe charge creation
        mock_charge_create.return_value = {"id": "ch_test_charge_id"}

        # Include sessionid cookie in the POST request to persist session data
        response = client.post(
            reverse("checkout:check_out"), {"stripeToken": "test_stripe_token"}
        )

        # Assertions
        assert response.status_code == 302  # Redirect after success
        assert response.url == reverse("checkout:check_out")  # Redirect URL
        payment = Payment.objects.get(cart=cart)
        assert payment.cart.cartitem_set.all().count() == 1
        assert payment.stripe_customer_id == "cus_existing_customer_id"

    def test_post_checkout_invalid_stripe_token(self, setup_session: Client):
        """Test invalid request method for checkout view."""

        client = setup_session

        # Attempt POST without stripeToken
        response = client.post(reverse("checkout:check_out"))
        assert response.url == reverse("checkout:check_out")

    @patch("checkout.views.stripe.Customer.search")
    def test_checkout_view_post_stripe_error(
        self, mock_customer_search, setup_session: Client, cart: CartFactory, mocker
    ):

        client = setup_session
        # Mock Stripe customer search to return an existing customer
        mock_customer_search.return_value = {"data": []}
        # Mock Stripe's Customer.create to raise an error
        mocker.patch(
            "checkout.views.stripe.Customer.create",
            side_effect=Exception("Stripe error"),
        )

        response = client.post(
            reverse("checkout:check_out"), {"stripeToken": "test_token"}
        )

        assert response.url == reverse("checkout:check_out")

    def test_checkout_view_post_no_cart(
        self, setup_session_without_CartItems: Client, user: CustomUserOnlyFactory
    ):

        client = setup_session_without_CartItems

        client.force_login(user)

        response = client.post(
            reverse("checkout:check_out"), {"stripeToken": "test_token"}
        )
        assert response.status_code == 400
        assert response.json() == {"error": "No active cart found"}


@pytest.mark.django_db
class Test_StripeWebHook:

    def test_stripe_webhook_charge_succeeded(
        self,
        setup_session_with_quantity_three: Client,
        cart: CartFactory,
        user: CustomUserOnlyFactory,
    ):

        # Create a user, session, and a cart using Factory Boy
        client = setup_session_with_quantity_three

        # Create a Stripe `charge.succeeded` webhook event payload
        payload = {
            "type": "charge.succeeded",
            "data": {
                "object": {
                    "id": "ch_1FvG8SB1vMbFJGQmNj6Gl9Zl",
                    "metadata": {
                        "user_id": str(user.id),
                        "cart_id": str(cart.id),
                    },
                    # ...other charge details
                }
            },
        }

        # create a Payment object
        payment_object = PaymentFactory(cart=cart, user=user)

        # Send POST request with payload
        response = client.post(
            reverse("checkout:stripe_webhook"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # Assert response status code and content
        assert response.status_code == 200
        response_content = response.json()
        assert response_content["message"] == "stripe created"
        payment_object = Payment.objects.get(id=payment_object.id)
        assert payment_object.payment_status == "SUCCESSFUL"

    def test_stripe_webhook_charge_refunded(
        self,
        setup_session_with_quantity_three: Client,
        cart: CartFactory,
        user: CustomUserOnlyFactory,
    ):

        # Create a user, session, and a cart using Factory Boy
        client = setup_session_with_quantity_three

        # fetch the Cartitem for refund
        cartitem = cart.cartitem_set.first()

        # Create a Stripe `charge.refunded` webhook event payload
        payload = {
            "type": "charge.refunded",
            "data": {
                "object": {
                    "id": "ch_1FvG8SB1vMbFJGQmNj6Gl9Zl",
                    "metadata": {
                        "user_id": str(user.id),
                        "cartitem_id": str(cartitem.id),
                    },
                    # ...other refund details
                }
            },
        }

        # Send POST request with payload
        response = client.post(
            reverse("checkout:stripe_webhook"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # Assert response status code and content
        assert response.status_code == 200

        # Assert that the Refund was created
        refunded_object = Refund.objects.get(cartitem=cartitem)
        assert refunded_object.stripe_refund_id == "ch_1FvG8SB1vMbFJGQmNj6Gl9Zl"
        assert refunded_object.refund_status == "REFUNDED"

    def test_stripe_webhook_invalid_payload(self, client: Client):
        # Invalid payload (not a valid JSON format)
        payload = "invalid_payload"

        # Send POST request with payload
        response = client.post(
            reverse("checkout:stripe_webhook"),
            data=payload,
            content_type="application/json",
        )

        # Assert response status code for invalid payload
        assert response.status_code == 400

    def test_stripe_webhook_unhandled_event(self, client: Client):
        # Create a Stripe unhandled webhook event payload
        payload = {
            "type": "some_unhandled_event",
            "data": {
                "object": {
                    "id": "unhandled_event",
                }
            },
        }

        # Send POST request with payload
        response = client.post(
            reverse("checkout:stripe_webhook"),
            data=payload,
            content_type="application/json",
        )

        # Assert response status code and content
        assert response.status_code == 200
        response_content = response.json()
        assert response_content == {}


@pytest.mark.django_db
class Test_ViewOrders:

    def test_get_view_orders_with_payments(
        self,
        setup_session_with_quantity_three: Client,
        user: CustomUserOnlyFactory,
        cart: CartFactory,
    ):
        """Test to verify the GET request with carts and payments."""
        client = setup_session_with_quantity_three

        # Create payments for the user
        PaymentFactory(user=user, cart=cart, payment_status="SUCCESSFUL")

        # Send a GET request to the view orders URL
        response = client.get(reverse("checkout:view_orders"))

        # Assertions
        assert response.status_code == 200
        assert "carts" in response.context
        assert "payment_objects" in response.context

        carts = response.context["carts"]
        payments = response.context["payment_objects"]

        # Verify that the carts and payment objects are returned in the context
        assert carts.count() == 1
        assert payments.count() == 1

    def test_get_view_orders_without_payments(
        self, setup_session_with_quantity_three: Client
    ):
        """Test to verify the GET request when there are no payments."""

        client = setup_session_with_quantity_three

        # Send a GET request to the view orders URL
        response = client.get(reverse("checkout:view_orders"))

        # Assertions
        assert response.status_code == 200
        assert "carts" in response.context
        assert "payment_objects" in response.context

        # Verify that there are carts but no payments
        carts = response.context["carts"]
        payments = response.context["payment_objects"]

        # those cart for which "cart_payment" is NULL ==> payment object not created
        assert carts.count() == 0
        assert payments is None

    def test_get_view_orders_no_carts(
        self, setup_session_with_quantity_three: Client, user: CustomUserOnlyFactory
    ):
        """Test to verify the GET request when there are no carts for the user."""
        client = setup_session_with_quantity_three

        # Remove all cart objects for the user
        Cart.objects.filter(user=user).delete()

        # Send a GET request to the view orders URL
        response = client.get(reverse("checkout:view_orders"))

        # Assertions
        assert response.status_code == 200
        assert "carts" in response.context
        assert "payment_objects" in response.context

        # Verify that there are no carts and no payments
        carts = response.context["carts"]
        payments = response.context["payment_objects"]

        assert not carts.exists()
        assert payments is None


@pytest.mark.django_db
class Test_ChargeRefundView:

    @patch("checkout.views.stripe.Charge.retrieve")
    @patch("checkout.views.stripe.Charge.modify")
    @patch("checkout.views.stripe.Refund.create")
    def test_successful_refund(
        self,
        mock_refund_create,
        mock_charge_modify,
        mock_charge_retrieve,
        setup_session_with_quantity_three: Client,
        cart: CartFactory,
        cart_item_creation_with_monitor,
        user: CustomUserOnlyFactory,
    ):
        """Test the successful refund of a charge."""
        client = setup_session_with_quantity_three

        cartitem = cart_item_creation_with_monitor

        # create a Payment object for this cartitem
        payment = PaymentFactory(user=user, cart=cart, payment_status="SUCCESSFUL")

        # Mock Stripe API responses
        mock_charge_retrieve.return_value = {"id": "ch_test_charge_id"}
        mock_refund_create.return_value = {"id": "re_test_refund_id"}

        # Send GET request to refund view
        response = client.get(reverse("checkout:refund", kwargs={"id": cartitem.id}))

        # Assertions
        assert response.status_code == 302

        mock_charge_retrieve.assert_called_once_with(payment.stripe_charge_id)
        mock_refund_create.assert_called_once_with(
            charge=payment.stripe_charge_id,
            amount=int(cartitem.price),
            metadata={
                "user_id": user.id,
                "cartitem_id": cartitem.id,
            },
        )

    @patch("checkout.views.stripe.Charge.retrieve")
    @patch("checkout.views.stripe.Charge.modify")
    @patch("checkout.views.stripe.Refund.create")
    def test_charge_retrieve_failure(
        self,
        mock_refund_create,
        mock_charge_modify,
        mock_charge_retrieve,
        setup_session_with_quantity_three: Client,
        cart_item_creation_with_monitor,
        cart: CartFactory,
        user: CustomUserOnlyFactory,
    ):
        """Test failure when retrieving the charge from Stripe."""

        client = setup_session_with_quantity_three

        cartitem = cart_item_creation_with_monitor

        # create a Payment object for this cartitem
        payment = PaymentFactory(user=user, cart=cart, payment_status="SUCCESSFUL")

        # Mock Stripe charge retrieval to raise an error
        mock_charge_retrieve.side_effect = stripe.error.StripeError(
            "Error retrieving charge"
        )

        # Send GET request to refund view
        response = client.get(reverse("checkout:refund", kwargs={"id": cartitem.id}))

        # Assertions
        assert response.status_code == 302
        assert response.url == "/"
        messages = list(get_messages(response.wsgi_request))

        assert any(
            "Error retrieving charge from Stripe" in message.message
            for message in messages
        )
        mock_charge_retrieve.assert_called_once_with(payment.stripe_charge_id)
        mock_refund_create.assert_not_called()
        mock_charge_modify.assert_not_called()

    @patch("checkout.views.stripe.Charge.retrieve")
    @patch("checkout.views.stripe.Charge.modify")
    @patch("checkout.views.stripe.Refund.create")
    def test_refund_creation_failure(
        self,
        mock_refund_create,
        mock_charge_modify,
        mock_charge_retrieve,
        setup_session_with_quantity_three: Client,
        cart_item_creation_with_monitor,
        cart: CartFactory,
        user: CustomUserOnlyFactory,
    ):
        """Test failure when creating a refund."""

        client = setup_session_with_quantity_three

        cartitem = cart_item_creation_with_monitor

        # create a Payment object for this cartitem
        payment = PaymentFactory(user=user, cart=cart, payment_status="SUCCESSFUL")

        # Mock Stripe API responses
        mock_charge_retrieve.return_value = {"id": "ch_test_charge_id"}
        mock_refund_create.side_effect = stripe.error.StripeError(
            "Error creating refund"
        )

        # Send GET request to refund view
        response = client.get(reverse("checkout:refund", kwargs={"id": cartitem.id}))

        # Assertions
        assert response.status_code == 302
        assert response.url == "/"
        messages = list(get_messages(response.wsgi_request))

        assert any("Error refunding charge" in message.message for message in messages)

        mock_charge_retrieve.assert_called_once_with(payment.stripe_charge_id)
        mock_charge_modify.assert_called_once()
        mock_refund_create.assert_called_once_with(
            charge=payment.stripe_charge_id,
            amount=int(cartitem.price),
            metadata={
                "user_id": user.id,
                "cartitem_id": cartitem.id,
            },
        )
