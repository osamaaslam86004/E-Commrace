import factory
from faker import Factory
from Homepage.Homepage_factory import CustomUserOnlyFactory
from cart.models import Cart, CartItem
from django.contrib.contenttypes.models import ContentType
from tests.books.books_factory_classes import BookFormatFactory
from tests.i.factory_classes import MonitorsFactory

fake = Factory.create()


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(CustomUserOnlyFactory)
    subtotal = factory.LazyAttribute(
        lambda _: fake.pyfloat(right_digits=2, positive=True)
    )
    total = factory.LazyAttribute(lambda _: fake.pyfloat(right_digits=2, positive=True))


class CartItemBase(factory.DjangoModelFactory):
    object_id = factory.SelfAttribute("content_object.id")
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )
    quantity = factory.LazyAttribute(lambda _: fake.pyint(min_value=1, max_value=10))
    price = factory.LazyAttribute(lambda _: fake.pyfloat(right_digits=2, positive=True))

    class Meta:
        exclude = ["content_object"]
        abstract = True


class CartItemMonitorsFactory(CartItemBase):
    class Meta:
        model = CartItem

    content_object = factory.SubFactory(MonitorsFactory)


class CartItemBooksFactory(CartItemBase):
    class Meta:
        model = CartItem

    content_object = factory.SubFactory(BookFormatFactory)
