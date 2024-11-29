import logging

import factory
import factory.django
from django.contrib.contenttypes.models import ContentType
from factory.django import DjangoModelFactory
from faker import Faker

from book_.models import BookFormat
from cart.models import Cart, CartItem
from i.models import Monitors
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory

fake = Faker()
# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)


class CartFactory(DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(CustomUserOnlyFactory)
    subtotal = factory.Sequence(lambda n: n * 10.0)
    total = factory.Sequence(lambda n: n * 10.0)


class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )
    # Set the object_id based on the type of content_object
    object_id = factory.LazyAttribute(
        lambda o: (
            o.content_object.monitor_id
            if isinstance(o.content_object, Monitors)
            else o.content_object.id
        )
    )

    content_object = factory.Maybe(
        factory.SubFactory(Monitors),
        factory.SubFactory(BookFormat),
    )
    quantity = factory.Sequence(lambda n: n + 1)
    price = factory.LazyAttribute(lambda o: o.content_object.price)
