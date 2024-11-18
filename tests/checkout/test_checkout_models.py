import pytest
from django.contrib.auth import get_user_model

from cart import cart_items
from checkout.models import Payment, Refund
from tests.cart.factory_classes import CartFactory, CartItemFactory
from tests.checkout.factory_classes import PaymentFactory, RefundFactory
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i.factory_classes import (ComputerSubCategoryFactory,
                                     MonitorsFactory, ProductCategoryFactory)


@pytest.mark.django_db
class Test_PaymentAndRefundModels:

    @pytest.fixture
    def setup_user_and_cart(self):
        # Create a user
        user = CustomUserOnlyFactory(user_type="SELLER", password="User 1122334455!")
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

        # Create a cart for the user
        cart = CartFactory(user=user)
        assert cart is not None

        return user, monitor, cart

    def test_create_payment(self, setup_user_and_cart):
        user, monitor, cart = setup_user_and_cart

        # Create a payment instance using the factory
        payment = PaymentFactory(user=user, cart=cart, payment_status="PENDING")

        # Assertions to verify the payment instance
        assert payment.user == user
        assert payment.cart == cart
        assert payment.payment_status == "PENDING"  # Default value
        assert payment.stripe_charge_id is not None
        assert payment.stripe_customer_id is not None
        assert payment.timestamp is not None

    def test_create_refund(
        self,
        setup_user_and_cart: tuple[CustomUserOnlyFactory, MonitorsFactory, CartFactory],
    ):
        user, monitor, cart = setup_user_and_cart

        # Create a cart item for the refund
        cart_item = CartItemFactory(content_object=monitor)
        assert cart_item is not None

        # Create a refund instance using the factory
        refund = RefundFactory(cart=cart, cartitem=cart_item)

        # Assertions to verify the refund instance
        assert refund.cart == cart
        assert refund.cartitem == cart_item
        assert refund.refund_status == "REFUNDED"  # Default value
        assert refund.stripe_refund_id is not None

    def test_payment_refund_relationship(self, setup_user_and_cart):
        user, monitor, cart = setup_user_and_cart

        # Create a payment instance
        payment = PaymentFactory(user=user, cart=cart)

        # Create a refund instance related to the same cart
        cart_item = CartItemFactory(content_object=monitor)
        assert cart_item is not None

        refund = RefundFactory(cart=cart, cartitem=cart_item)

        # Assertions to verify the relationships
        assert payment.user == user
        assert refund.cart == cart
        assert refund.cartitem == cart_item
        assert refund.cart == payment.cart  # Refund should relate to the same cart
