import factory
from factory import SubFactory
from faker import Faker

from checkout.models import Payment, Refund
from tests.cart.factory_classes import CartFactory, CartItemFactory
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory

fake = Faker()


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    user = SubFactory(CustomUserOnlyFactory)
    cart = SubFactory(CartFactory)
    stripe_charge_id = factory.LazyFunction(
        fake.uuid4
    )  # Use LazyFunction with the Faker instance
    stripe_customer_id = factory.LazyFunction(
        fake.uuid4
    )  # Use LazyFunction with the Faker instance
    payment_status = factory.Iterator([choice[0] for choice in Payment.CHARGE_STATUS])
    timestamp = factory.LazyFunction(
        fake.date_time
    )  # Use LazyFunction with the Faker instance


class RefundFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Refund

    cart = SubFactory(CartFactory)
    cartitem = SubFactory(CartItemFactory)
    stripe_refund_id = factory.LazyFunction(
        fake.uuid4
    )  # Use LazyFunction with the Faker instance
    refund_status = factory.Iterator([choice[0] for choice in Refund.REFUND_CHOICES])
