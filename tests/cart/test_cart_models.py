import pytest

from book_.models import BookFormat
from i.models import Monitors
from tests.books.books_factory_classes import (BookAuthorNameFactory,
                                               BookFormatFactory)
from tests.cart.factory_classes import CartFactory, CartItemFactory
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i.factory_classes import (ComputerSubCategoryFactory,
                                     MonitorsFactory, ProductCategoryFactory)


@pytest.fixture
def user_factory():
    return CustomUserOnlyFactory(user_type="SELLER")


@pytest.mark.django_db
def test_cart_creation(user_factory):

    user = user_factory

    cart = CartFactory(user=user, subtotal=100, total=100)
    assert cart.user.email == user.email
    assert cart.subtotal == 100
    assert cart.total == 100


@pytest.mark.django_db
def test_cart_item_creation_with_monitor(user_factory):

    user = user_factory

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
    # create a cart item
    cart_item = CartItemFactory(content_object=monitor)

    assert Monitors.objects.all().count() == 1

    # retrieve the monitor
    retrieved_monitor = Monitors.objects.get(user=user)

    assert cart_item.content_object == retrieved_monitor
    assert cart_item.price == retrieved_monitor.price


@pytest.mark.django_db
def test_cart_item_creation_with_book_format(user_factory):

    # create user
    user = user_factory

    # Create a Product category for books
    product_category = ProductCategoryFactory(name="BOOKS")
    assert product_category is not None

    # Setup data for the tests
    author = BookAuthorNameFactory(author_name="John Doe", book_name="Python Mastery")
    # Create book formats to cover various filtering scenarios
    book_format = BookFormatFactory(
        book_author_name=author,
        user=user,
        product_category=product_category,
        price=50.00,
        is_new_available=True,
        is_used_available=False,
    )

    # create a cart item
    cart_item = CartItemFactory(content_object=book_format)

    assert BookFormat.objects.all().count() == 1
    # retrieve the monitor
    retrieved_book = BookFormat.objects.get(user=user)

    assert cart_item.content_object == retrieved_book
    assert cart_item.price == retrieved_book.price
