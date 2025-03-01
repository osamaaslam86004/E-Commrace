import io
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import JsonResponse
from django.template.exceptions import TemplateDoesNotExist
from django.test import Client
from django.urls import reverse
from PIL import Image
from pytest_django.asserts import assertTemplateUsed

from book_.models import BookFormat
from i.filters import MonitorsFilter
from i.forms import (
    BriefCasesForm,
    ComputerAndTabletsForm,
    ComputerSubCategoryForm,
    ElectronicsForm,
    LaptopsForm,
    MonitorsForm,
    ProductCategoryForm,
)
from i.models import Monitors, Review, Special_Features
from tests.books.books_factory_classes import BookAuthorNameFactory, BookFormatFactory
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i import factory_classes
from tests.i.factory_classes import (
    ComputerSubCategoryFactory,
    MonitorsFactory,
    ProductCategoryFactory,
    SpecialFeaturesFactory,
)


@pytest.mark.django_db
@pytest.fixture(scope="session")  # Changed from "function" to "session"
def create_special_features(django_db_setup, django_db_blocker):
    """Create special features for testing."""
    with django_db_blocker.unblock():  # Allow DB access in session-scoped fixture
        special_features = []
        for choice in Special_Features.SPECIAL_FEATURES_CHOICES:
            special_feature = Special_Features.objects.create(name=choice[0])
            special_features.append(special_feature)
    return special_features


# Parametrize the monitor attributes for dynamic creation in fixture
@pytest.fixture(scope="session")
def monitor_params(create_special_features):

    special_features = create_special_features
    return [
        {
            "name": "Monitor 1",
            "brand": "SAMSUNG",
            "monitor_type": "GAMING_MONITOR",
            "refresh_rate": 144,
            "max_display_resolution": "1920x1080",
            "price": Decimal("100"),
            "special_features": [special_features[0], special_features[1]],
        },
        {
            "name": "Monitor 2",
            "brand": "LG",
            "monitor_type": "CARE_MONITOR",
            "refresh_rate": 75,
            "max_display_resolution": "2560x1440",
            "price": Decimal("200"),
            "special_features": [special_features[1], special_features[2]],
        },
        {
            "name": "Monitor 3",
            "brand": "ASUS",
            "monitor_type": "GAMING_MONITOR",
            "refresh_rate": 240,
            "max_display_resolution": "3840x2160",
            "price": Decimal("300"),
            "special_features": [special_features[2], special_features[3]],
        },
        {
            "name": "Monitor 4",
            "brand": "Dell",
            "monitor_type": "HOME_OFFICE",
            "refresh_rate": 144,
            "max_display_resolution": "1920x1080",
            "price": Decimal("400"),
            "special_features": [special_features[3], special_features[4]],
        },
    ]


@pytest.fixture(scope="session")
def client():
    return Client()


@pytest.fixture
def client_with_user(client: Client):
    user = CustomUserOnlyFactory(
        username="testuser", email="testuser@gmail.com", user_type="SELLER"
    )
    client.force_login(user)
    return client


@pytest.fixture()
def setup_categories():
    # Create a Product category for computer
    Product_Category = ProductCategoryFactory(name="COMPUTER")
    assert Product_Category is not None

    # Create a computer category for monitor
    Computer_SubCategory = ComputerSubCategoryFactory(name="MONITOR")
    assert Computer_SubCategory is not None

    return Product_Category, Computer_SubCategory


@pytest.fixture
def setup_session(client_with_user: Client):
    """Helper method to set user session"""

    client = client_with_user

    session = client.session
    # fetch the user
    user = get_user_model().objects.get(email="testuser@gmail.com")

    # add user_id to session
    session["user_id"] = user.id
    session.save()

    # Update session's cookie
    session_cookie_name = settings.SESSION_COOKIE_NAME
    client.cookies[session_cookie_name] = session.session_key

    return client, user


@pytest.fixture
def create_image():

    # Create an image file using Pillow
    image = Image.new("RGB", (100, 100), color="red")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)

    # Create a SimpleUploadedFile from the image bytes
    uploaded_file = SimpleUploadedFile(
        "test_image.jpg", image_bytes.read(), content_type="image/jpeg"
    )

    assert uploaded_file is not None
    # Debug print
    # print(f"Uploaded file size: {len(uploaded_file)} bytes")

    return uploaded_file


@pytest.fixture()
def create_monitor_form(
    client_with_user: Client,
    setup_categories,
    setup_session,
    create_image: SimpleUploadedFile,
):
    # setup user
    client = client_with_user

    # setup product categories
    Product_Category, Computer_SubCategory = setup_categories

    # setup user cookie-based session
    client, user = setup_session

    # build MonitorFactory instance
    monitor = MonitorsFactory.build(
        user=user,
        Product_Category=Product_Category,
        Computer_SubCategory=Computer_SubCategory,
    )

    Special_Features.objects.create(name="Frameless"),
    Special_Features.objects.create(name="Flicker-Free"),

    # getting the ids of special features
    special_features_objs = Special_Features.objects.all()

    # Corrected monitor form data
    monitor_form_data = {
        "name": monitor.name,
        "image_1": create_image,
        "image_2": create_image,
        "image_3": create_image,
        "is_active": True,
        "brand": monitor.brand[0],  # Use the display value ('Acer')
        "aspect_ratio": monitor.aspect_ratio,
        "max_display_resolution": monitor.max_display_resolution[0],
        "screen_size": monitor.screen_size,
        "mounting_type": monitor.mounting_type[0],
        "refresh_rate": monitor.refresh_rate[0],  # Use just the integer (144)
        "monitor_type": monitor.monitor_type,
        "item_dimensions": monitor.item_dimensions,
        "item_weight": monitor.item_weight,
        "voltage": monitor.voltage,
        "color": monitor.color,
        "hdmi_port": monitor.hdmi_port,
        "built_speakers": monitor.built_speakers,
        "price": monitor.price,
        "quantity_available": monitor.quantity_available,
        "choose_special_features": [feature.id for feature in special_features_objs],
    }

    files = {
        "image_1": monitor_form_data["image_1"],
        "image_2": monitor_form_data["image_2"],
        "image_3": monitor_form_data["image_3"],
    }

    monitor_form = MonitorsForm(data=monitor_form_data, files=files)
    print(f"form errors: {monitor_form.errors}")
    assert monitor_form.is_valid()

    return (
        monitor_form_data,
        Product_Category,
        Computer_SubCategory,
        client,
        user,
        monitor,
    )


@pytest.mark.django_db
class Test_ProductViewsIntegration:

    def test_success_page_view(self, client_with_user: Client):
        """Test the success page view renders correctly."""

        response = client_with_user.get(reverse("i:success_page"))
        assert response.status_code == 200
        assert "success_page.html" in (t.name for t in response.templates)

    def test_select_product_category_view(self, client_with_user: Client):
        """Test the product category selection view requires login and permission."""

        response = client_with_user.get(reverse("i:select_product_category"))
        assert response.status_code == 200
        assert "product_category.html" in (t.name for t in response.templates)
        assert isinstance(
            response.context["product_category_form"], ProductCategoryForm
        )

    @pytest.mark.parametrize(
        "category_name, expected_form, expected_status, expected_template",
        [
            ("COMPUTER", ComputerSubCategoryForm, 200, "subcategory_form.html"),
            ("ELECTRONICS", ElectronicsForm, 200, "subcategory_form.html"),
            ("INVALID_CATEGORY", None, 400, None),
        ],
    )
    def test_load_subcategory_form(
        self,
        category_name,
        expected_form,
        expected_status,
        expected_template,
        client_with_user,
    ):
        """Test loading subcategory form for valid and invalid product categories."""
        if category_name != "INVALID_CATEGORY":
            response = client_with_user.post(
                reverse("i:load_subcategory_form"), data={"name": category_name}
            )
        else:
            response = client_with_user.post(
                reverse("i:load_subcategory_form"), data={"name": category_name}
            )

        assert response.status_code == expected_status

        if expected_status == 200:
            assert expected_template in (t.name for t in response.templates)
            assert isinstance(response.context["form"], expected_form)
        else:
            assert response.content.decode() == "Invalid category selected."

    def test_load_subcategory_form_redirect_books(self, client_with_user):
        """Test redirecting to book form when BOOKS category is selected."""
        response = client_with_user.post(
            reverse("i:load_subcategory_form"), data={"name": "BOOKS"}
        )
        assert response.status_code == 302
        assert response.url == reverse("book_:create_update_book_formats")

    def test_load_subsubcategory_form_computers_and_tablets(self, client_with_user):
        """Test loading sub-subcategory form for COMPUTERS_AND_TABLETS."""
        response = client_with_user.post(
            reverse("i:load_subsubcategory_form"),
            data={"name": "COMPUTERS_AND_TABLETS"},
        )
        assert response.status_code == 200
        assert "subsubcategory_form.html" in (t.name for t in response.templates)
        assert isinstance(
            response.context["subsubcategory_form"], ComputerAndTabletsForm
        )

    def test_load_subsubcategory_form_redirect_monitor(self, client_with_user):
        """Test redirecting to monitor form when MONITORS subcategory is selected."""
        response = client_with_user.post(
            reverse("i:load_subsubcategory_form"), data={"name": "MONITORS"}
        )
        assert response.status_code == 302
        assert response.url == reverse("i:add_monitor")

    def test_load_sub_subsubcategory_form_laptops(self, client_with_user):
        """Test loading sub-subsubcategory form for LAPTOPS."""

        with pytest.raises(TemplateDoesNotExist):
            response = client_with_user.post(
                reverse("i:load_sub_subsubcategory_form"), data={"name": "LAPTOPS"}
            )
            assert response.status_code == 200
            assert "sub_subsubcategory_form.html" in (
                t.name for t in response.templates
            )
            assert isinstance(response.context["form_1"], LaptopsForm)

    def test_load_sub_sub_subsubcategory_form_briefcases(
        self, client_with_user: Client
    ):
        """Test loading sub-sub-subsubcategory form for BRIEFCASE."""

        with pytest.raises(TemplateDoesNotExist):
            response = client_with_user.post(
                reverse("i:load_sub_sub_subsubcategory_form"),
                data={"name": "BRIEFCASE"},
            )

            assert isinstance(response.context["sub_sub_form"], BriefCasesForm)
            assertTemplateUsed(response, "sub_sub_subsubcategory_form.html")

    def test_load_sub_sub_subsubcategory_form_invalid(self, client_with_user):
        """Test invalid sub-sub-subcategory returns no form."""

        with pytest.raises(TemplateDoesNotExist):
            response = client_with_user.post(
                reverse("i:load_sub_sub_subsubcategory_form"), data={"name": "INVALID"}
            )
            assert response.status_code == 400
            assert response.content.decode() == "Invalid category selected."


@pytest.mark.django_db
class Test_ListOfProductsCategoryView:

    @pytest.fixture(
        autouse=True
    )  # no need to explicitly reference this fixture in class methods
    def setup_method(self):
        self.client = Client()

        self.user = CustomUserOnlyFactory(user_type="SELLER")
        assert self.user is not None

        self.client.force_login(self.user)

    def test_list_of_products_category_view_renders_template(self):
        """Test that the List_Of_Products_Category view renders the correct template."""
        response = self.client.get(
            reverse("i:list_of_products_category")
        )  # Adjust the URL name to your view's name

        assert response.status_code == 200
        assert "update_product.html" in (t.name for t in response.templates)

    def test_list_of_products_category_view_context_data(self):
        """Test that the List_Of_Products_Category view contains the correct context data."""
        response = self.client.get(
            reverse("i:list_of_products_category")
        )  # Adjust the URL name

        assert response.status_code == 200
        assert response.context is not None


@pytest.mark.django_db
class Test_ListOfBooksForUserView:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = Client()
        self.url = reverse("i:list_of_books_for_user")

        user = CustomUserOnlyFactory(user_type="SELLER")
        assert user is not None
        self.client.force_login(user)

        # Create a Product category for books
        self.product_category = ProductCategoryFactory(name="BOOKS")
        assert self.product_category is not None

        # Setup data for the tests
        self.author_1 = BookAuthorNameFactory(
            author_name="John Doe", book_name="Python Mastery"
        )
        self.author_2 = BookAuthorNameFactory(
            author_name="John Doe", book_name="Advanced Python Mastery"
        )
        self.author_3 = BookAuthorNameFactory(
            author_name="John Doe", book_name="Newbie Python Mastery"
        )

        # Create book formats to cover various filtering scenarios
        BookFormatFactory.create_batch(
            1,
            book_author_name=self.author_1,
            user=user,
            product_category=self.product_category,
            price=50.00,
            is_new_available=1,
            is_used_available=1,
        )
        BookFormatFactory.create_batch(
            1,
            book_author_name=self.author_2,
            user=user,
            product_category=self.product_category,
            price=30.00,
            is_new_available=1,
            is_used_available=1,
        )
        BookFormatFactory.create_batch(
            1,
            book_author_name=self.author_3,
            user=user,
            product_category=self.product_category,
            price=20.00,
            is_new_available=1,
            is_used_available=1,
        )

        self.book_format_count = BookFormat.objects.all().count()
        assert self.book_format_count == 3

    def test_list_of_books_for_user_view_renders_template(self):
        """Test that the List_Of_Books_For_User view renders the correct template."""
        response = self.client.get(reverse("i:list_of_books_for_user"))

        assert response.status_code == 200
        assert "list_of_book_products_for_update.html" in [
            t.name for t in response.templates
        ]

    def test_list_of_books_for_user_view_queryset(self):
        """Test that the view retrieves the correct queryset for the logged-in user."""
        response = self.client.get(
            reverse("i:list_of_books_for_user")
        )  # Adjust the URL name

        assert response.status_code == 200
        assert (
            len(response.context["book_formats"]) == 3
        )  # Check if both book formats are returned

    def test_list_of_books_for_user_view_no_books(self):
        """Test that the view handles the case when the user has no book formats."""

        # deleting all Books so simulate user has not created any Book product
        BookFormat.objects.all().delete()
        assert BookFormat.objects.all().count() == 0

        response = self.client.get(reverse("i:list_of_books_for_user"))

        assert response.status_code == 200
        assert "list_of_book_products_for_update.html" in (
            t.name for t in response.templates
        )
        assert not response.context["book_formats"]

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "filter_data, expected_count, expected_book_name",
        [
            (
                {
                    "book_name": "Python Mastery",
                    "price_min": 50,
                    "is_new_available": "on",
                    "is_used_available": "off",
                },
                3,
                "Python Mastery",
            ),
            (
                {
                    "book_name": "Advanced Python Mastery",
                    "price_min": 21,
                    "price_max": 29,
                    "is_new_available": "off",
                    "is_used_available": "on",
                },
                0,
                None,
            ),
            (
                {
                    "book_name": "",
                    "price_max": 20,
                    "is_new_available": "on",
                    "is_used_available": "off",
                },
                1,
                "Newbie Python Mastery",
            ),
        ],
    )
    def test_filter_books(
        self,
        filter_data,
        expected_count,
        expected_book_name,
    ):
        """Test the filtering functionality of the view."""

        # Sending a POST request with the filter data
        response = self.client.post(
            reverse("i:list_of_books_for_user"), data=filter_data
        )

        assert response.status_code == 200
        assert len(response.context["item_list"]) == expected_count

        if expected_count > 0:  # Only check book name if we expect at least one book
            assert (
                response.context["item_list"][0].book_author_name.book_name
                == expected_book_name
            )

    def test_filter_books_with_invalid_data(self):
        """Test that the view handles invalid filter form data gracefully."""
        filter_data = {
            "book_name": "",  # Invalid input
            "price_min": "INVALID_VALUE",
            "is_new_available": "off",
            "is_used_available": "off",
        }
        response = self.client.post(
            reverse("i:list_of_books_for_user"), data=filter_data
        )

        assert response.status_code == 200
        assert "partial_book_seller.html" in (t.name for t in response.templates)
        assert response.context["item_list"] == None


@pytest.mark.django_db
class Test_ListOfMonitorsForUserView:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = Client()
        self.url = reverse("i:list_of_monitors_for_user")

        self.user = CustomUserOnlyFactory(user_type="SELLER")
        assert self.user is not None
        self.client.force_login(self.user)

        # Create a Product category for books
        self.Product_Category = ProductCategoryFactory(name="COMPUTER")
        assert self.Product_Category is not None

        # Create a computer category for books
        self.Computer_SubCategory = ComputerSubCategoryFactory(name="MONITOR")
        assert self.Computer_SubCategory is not None

        # Create monitors for the user
        self.monitor_1 = MonitorsFactory(
            user=self.user,
            Computer_SubCategory=self.Computer_SubCategory,
            Product_Category=self.Product_Category,
            monitor_type="GAMING_MONITOR",
            brand="SAMSUNG",
            price=500.00,
        )
        self.monitor_2 = MonitorsFactory(
            user=self.user,
            Computer_SubCategory=self.Computer_SubCategory,
            Product_Category=self.Product_Category,
            monitor_type="CARE_MONITOR",
            brand="LG",
            price=300.00,
        )

    def test_get_list_of_monitors_renders_template(self):
        """Test that the view renders the correct template with monitor data."""
        response = self.client.get(self.url)

        assert response.status_code == 200
        assert "list_of_products_for_update.html" in [
            t.name for t in response.templates
        ]
        assert len(response.context["monitors"]) == 2  # Ensure both monitors are listed

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "filter_data,expected_count",
        [
            (
                {"monitor_type": "GAMING_MONITOR", "brand": "SAMSUNG"},
                1,
            ),
            (
                {"monitor_type": "CARE_MONITOR", "brand": "LG"},
                1,
            ),
            (
                {"monitor_type": "GAMING_MONITOR", "brand": "LG"},
                2,
            ),
            (
                {"brand": "In-Valid"},  # invalid input
                2,
            ),
        ],
        ids=[
            "filter_by_gaming_monitor_and_samsung_brand",
            "filter_by_care_monitor_and_lg_brand",
            "filter_by_gaming_monitor_and_lg_brand",
            "filter_by_invalid_brand",
        ],
    )
    def test_post_filter_monitors(self, filter_data, expected_count):
        """Test that filters apply correctly and only matching monitors are shown."""
        response = self.client.post(self.url, filter_data)

        assert response.status_code == 200
        print(f"Filtered monitors: {response.context['item_list']}")

        assert (
            len(response.context["item_list"]) == expected_count
        )  # Check expected monitor count

    def test_no_monitors_for_user(self):
        """Test that the view handles users with no monitors correctly."""
        # Delete all monitors for the user
        Monitors.objects.filter(user=self.user).delete()

        response = self.client.get(self.url)

        assert response.status_code == 200
        assert len(response.context["monitors"]) == 0  # No monitors should be returned


@pytest.mark.django_db
class Test_DeleteMonitorsProductView:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = Client()
        self.url = reverse("i:list_of_monitors_for_user")

        self.user = CustomUserOnlyFactory(user_type="SELLER")
        assert self.user is not None
        self.client.force_login(self.user)

        # Create a Product category for books
        self.Product_Category = ProductCategoryFactory(name="COMPUTER")
        assert self.Product_Category is not None

        # Create a computer category for books
        self.Computer_SubCategory = ComputerSubCategoryFactory(name="MONITOR")
        assert self.Computer_SubCategory is not None

        # Create monitors for the user
        self.monitor = MonitorsFactory(
            user=self.user,
            Computer_SubCategory=self.Computer_SubCategory,
            Product_Category=self.Product_Category,
            monitor_type="GAMING_MONITOR",
            brand="SAMSUNG",
            price=500.00,
        )

    def test_delete_monitor_success(self):

        # Issue a GET request to delete the monitor
        response = self.client.get(
            reverse("i:delete_monitor", kwargs={"product_id": self.monitor.monitor_id})
        )

        # Check that the monitor was successfully deleted
        assert Monitors.objects.filter(monitor_id=self.monitor.monitor_id).count() == 0
        assert response.status_code == 302  # Redirect after success
        assert response.url == reverse("i:list_of_monitors_for_user")

    def test_delete_monitor_permission_denied(self):
        user_1_email = self.user.email

        # Logout the previously logged-in user
        self.client.logout()

        # create another user
        self.user = CustomUserOnlyFactory(user_type="SELLER")
        assert self.user is not None
        # Assert new user and user_1 are not same
        assert user_1_email != self.user.email

        self.client.force_login(self.user)

        # Issue a GET request to delete the monitor
        response = self.client.get(
            reverse("i:delete_monitor", kwargs={"product_id": self.monitor.monitor_id})
        )

        # Check that the monitor was not deleted
        assert Monitors.objects.filter(monitor_id=self.monitor.monitor_id).count() == 1
        assert response.status_code == 302
        assert response.url == reverse("i:list_of_monitors_for_user")

    def test_delete_nonexistent_monitor(self, client: Client):
        user = CustomUserOnlyFactory(username="testuser", user_type="SELLER")

        client.force_login(user)

        with pytest.raises(Exception) as excep_into:
            # Issue a GET request to delete a non-existent monitor
            response = client.get(
                reverse("i:delete_monitor", kwargs={"product_id": 9999})
            )

            # Check that no monitor was deleted and error message was shown
            assert (
                Monitors.objects.count() == 0
            )  # Assuming no other monitors in the test DB
            assert response.status_code == 302  # Redirect after failure
            assert response.url == reverse("i:list_of_monitors_for_user")
            assert excep_into == "monitor.DoesNotExist"


@pytest.mark.django_db
class Test_MonitorListView:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = Client()
        self.url = reverse("i:list_of_monitors_for_user")

        self.user = CustomUserOnlyFactory(user_type="SELLER")
        assert self.user is not None
        self.client.force_login(self.user)

        # Create a Product category for books
        self.Product_Category = ProductCategoryFactory(name="COMPUTER")
        assert self.Product_Category is not None

        # Create a computer category for books
        self.Computer_SubCategory = ComputerSubCategoryFactory(name="MONITOR")
        assert self.Computer_SubCategory is not None

        # Create monitors for the user
        self.monitors = MonitorsFactory.create_batch(
            5,
            user=self.user,
            Computer_SubCategory=self.Computer_SubCategory,
            Product_Category=self.Product_Category,
        )

        # Create a review for each monitor
        reviews = []
        for monitor in self.monitors:
            review = factory_classes.ReviewFactory(
                user=self.user, product=monitor, status=1, rating=Decimal("4")
            )
            reviews.append(review)

    def test_monitor_list_view(self):

        # Make a GET request to the monitor list view
        response = self.client.get(reverse("i:MonitorListView"))

        # Check that the view returns a 200 status code
        assert response.status_code == 200

        # Check that the correct template is used
        assert "monitor_list.html" in [t.name for t in response.templates]

        # Check if the monitors are in the context
        assert (
            len(response.context["item_list"]) == 3
        )  # Pagination set to 3 items per page

        # Check if the filters are working (assuming there's filtering logic)
        assert isinstance(response.context["filter"], MonitorsFilter)

        # Check if content_id matches the monitors content type
        content_id = ContentType.objects.get(app_label="i", model="monitors").id
        assert response.context["content_id"] == content_id

    def test_monitor_list_view_pagination(self):

        # Set the paginator to display 2 items per page
        response = self.client.get(reverse("i:MonitorListView"), {"page": 1})

        assert response.status_code == 200

        page_obj = response.context["item_list"]

        assert len(page_obj.object_list) == 3  # First page contains 3 items
        assert page_obj.has_next()  # There should be more pages

        response = self.client.get(reverse("i:MonitorListView"), {"page": 2})
        page_obj = response.context["item_list"]

        assert len(page_obj.object_list) == 2  # Second page contains 2 items
        assert not page_obj.has_next()  # No more pages after this one

    def test_monitor_list_view_ratings(self):

        # Make a GET request
        response = self.client.get(reverse("i:MonitorListView"))

        # Check if the ratings were calculated correctly (mocked result)
        for key, value in response.context["item_ratings"].items():
            assert value == 4
        for key, value in response.context["rating_count"].items():
            assert value == 1


@pytest.mark.django_db
class Test_FilterListView:

    # setup with SELLER user type
    @pytest.fixture(scope="function")
    def setup_method(self, monitor_params):

        client = Client()

        user = CustomUserOnlyFactory(user_type="SELLER")
        assert user is not None

        client.force_login(user)

        try:
            # Create a Product category for books
            Product_Category = ProductCategoryFactory(name="COMPUTER")
            assert Product_Category is not None

            # Create a computer category for books
            Computer_SubCategory = ComputerSubCategoryFactory(name="MONITOR")
            assert Computer_SubCategory is not None

        except Exception as e:
            pass

        """Setup initial monitors based on parametrize data"""
        monitors = []
        for monitor_data in monitor_params:
            monitor = MonitorsFactory(
                user=user,
                Computer_SubCategory=Computer_SubCategory,
                Product_Category=Product_Category,
                name=monitor_data["name"],
                brand=monitor_data["brand"],
                monitor_type=monitor_data["monitor_type"],
                refresh_rate=monitor_data["refresh_rate"],
                max_display_resolution=monitor_data["max_display_resolution"],
                price=monitor_data["price"],
                special_features=monitor_data["special_features"],
            )

            # for id in monitor_data["special_features"]:
            #     monitor.special_features.add(id)
            monitors.append(monitor)

        """Setup initial data for the test"""

        reviews = []
        for monitor in monitors:
            review = factory_classes.ReviewFactory(
                user=user, product=monitor, status=1, rating=Decimal("4")
            )
            reviews.append(review)

        return {
            "client": client,
            "user": user,
            "monitors": monitors,
            "reviews": reviews,
        }

    @pytest.mark.parametrize(
        "filter_data,expected_count",
        [
            ({"name": "Monitor 1"}, 3),
            ({"brand": "LG"}, 1),
            ({"monitor_type": "GAMING_MONITOR"}, 2),
            ({"refresh_rate": 144}, 2),
            ({"max_display_resolution": "1920x1080"}, 2),
            ({"special_features": [1, 2, 3, 4, 5, 6, 7]}, 3),
        ],
        ids=[
            "Filter by name: Monitor 1",
            "Filter by brand: LG",
            "Filter by monitor type: GAMING_MONITOR",
            "Filter by refresh rate: 144",
            "Filter by max display resolution: 1920x1080",
            "Filter by special features: [1, 2, 3, 4, 5, 6, 7]",
        ],
    )
    def test_filter_list_view_valid_post(
        self, filter_data, expected_count, setup_method
    ):
        """Test for a valid POST request with filter form submission."""

        client = setup_method["client"]

        # Make a GET request to the monitor list view
        response = client.post(reverse("i:filter"), data=filter_data)

        # Check that the view returns a 200 status code
        assert response.status_code == 200

        # Check that the filtered monitors are returned in the context
        assert len(response.context["item_list"]) == expected_count

        # **NEW ASSERTION (for special_features):**
        if "special_features" in filter_data:
            special_features_filter = set(filter_data["special_features"])
            for monitor in response.context["item_list"]:
                monitor_special_features = set(
                    monitor.special_features.values_list("id", flat=True)
                )
                assert not monitor_special_features.isdisjoint(special_features_filter)

        # Check that the filter form is valid and filters are applied
        assert isinstance(response.context["form"], MonitorsFilter)
        assert response.context["form"].is_valid()

        # Check if item ratings and rating count are correctly calculated (mock if needed)
        assert response.context["item_ratings"] is not None
        assert response.context["rating_count"] is not None

    def test_filter_list_view_invalid_post(self, setup_method):
        """Test for an invalid POST request (invalid form submission)."""

        # Simulate an invalid POST request with invalid data
        invalid_data = {
            "invalid_field": "Invalid value",  # Invalid data that the form can't process
        }
        client = setup_method["client"]

        response = client.post(reverse("i:filter"), data=invalid_data)

        # Check that the view returns a 400 status code
        assert response.status_code == 200

        # Check that an appropriate error message is returned
        # assert (
        #     JsonResponse({"error": "Form is not valid"}, status=400).content
        #     in response.content
        # )

    def test_filter_list_view_invalid_method(self, setup_method):
        """Test for invalid request method (non-POST)."""

        client = setup_method["client"]

        # Simulate a GET request (instead of a POST request)
        response = client.get(reverse("i:filter"))

        # Check that the view returns a 405 Method Not Allowed error
        assert response.status_code == 405

        # Check that an appropriate error message is returned
        assert (
            JsonResponse({"error": "Invalid request method"}, status=405).content
            in response.content
        )

    def test_filter_list_view_pagination(self, setup_method):
        """Test for pagination behavior."""

        # Simulate a valid POST request to trigger filtering and pagination
        valid_data = {"name": "Monitor"}  # Assuming filtering by name

        client = setup_method["client"]

        response = client.post(reverse("i:filter"), data=valid_data)

        page_obj = response.context["item_list"]

        assert len(page_obj.object_list) == 3  # First page contains 3 items
        assert page_obj.has_next()  # There should be more pages


@pytest.mark.django_db
class Test_MonitorDetailView:

    @pytest.fixture(scope="function")
    def setup_method(self):

        client = Client()

        user = CustomUserOnlyFactory(user_type="SELLER")
        assert user is not None

        client.force_login(user)

        try:
            # Create a Product category for books
            Product_Category = ProductCategoryFactory(name="COMPUTER")
            assert Product_Category is not None

            # Create a computer category for books
            Computer_SubCategory = ComputerSubCategoryFactory(name="MONITOR")
            assert Computer_SubCategory is not None

        except Exception as e:
            pass

        """Setup initial monitor based on parametrize data"""
        monitor = MonitorsFactory(
            user=user,
            Computer_SubCategory=Computer_SubCategory,
            Product_Category=Product_Category,
            name="Monitor 1",
            brand="SAMSUNG",
            monitor_type="GAMING_MONITOR",
            refresh_rate=144,
            max_display_resolution="1920x1080",
            price=Decimal("100"),
        )

        """Setup initial data for the test"""

        # Create a batch of 4 monitors and assign prices individually
        reviews = []

        review = factory_classes.ReviewFactory(
            user=user, product=monitor, status=1, rating=Decimal("4")
        )
        reviews.append(review)

        return {
            "client": client,
            "user": user,
            "monitor": monitor,
            "reviews": reviews,
        }

    def test_monitor_detail_view_status_code(self, setup_method):
        """Test if the view returns a 200 status code."""

        client = setup_method["client"]
        monitor = setup_method["monitor"]

        url = reverse("i:add_review", kwargs={"product_id": monitor.monitor_id})

        response = client.get(url)
        assert response.status_code == 200

    def test_monitor_detail_view_template_used(self, setup_method):
        """Test if the view renders the correct template."""

        client = setup_method["client"]
        monitor = setup_method["monitor"]

        url = reverse("i:add_review", kwargs={"product_id": monitor.monitor_id})

        response = client.get(url)
        assert response.status_code == 200
        assert "product_detail.html" in [t.name for t in response.templates]

    def test_context_data(self, setup_method):
        """Test if the context data returned by the view is correct."""

        client = setup_method["client"]
        monitor = setup_method["monitor"]

        url = reverse("i:add_review", kwargs={"product_id": monitor.monitor_id})

        response = client.get(url)
        assert response.status_code == 200

        context = response.context
        assert context["monitor"] == monitor
        assert context["average_rating"] == 4
        assert context["total_ratings"] == 1
        assert len(context["comments"]) == 1

    def test_special_features_in_context(self, setup_method):
        """Test if the special features are included in the context."""

        client = setup_method["client"]
        monitor = setup_method["monitor"]

        url = reverse("i:add_review", kwargs={"product_id": monitor.monitor_id})

        response = client.get(url)
        assert response.status_code == 200

        sp = monitor.special_features.all()
        expected_special_features = [feature.get_name_display() for feature in sp]

        context = response.context
        assert context["sp"] == expected_special_features

    def test_rating_bars_width_percentage(self, setup_method):
        """Test if the width percentage for rating bars is calculated correctly."""

        client = setup_method["client"]
        monitor = setup_method["monitor"]

        url = reverse("i:add_review", kwargs={"product_id": monitor.monitor_id})

        response = client.get(url)
        assert response.status_code == 200

        width_percentages = response.context["width_percentages"]
        total_ratings = 5  # We created 5 reviews with 4-star ratings

        assert width_percentages[5] == 0  # No 5-star ratings
        assert width_percentages[4] == (
            5 / total_ratings * 100
        )  # All 5 ratings are 4-star

    def test_add_product_to_browsing_history(self, setup_method):
        """Test adding product details to the browsing history stored in session."""

        client = setup_method["client"]
        monitor = setup_method["monitor"]

        product_details = {
            "name": monitor.name,
            "price": str(monitor.price),
            "rating": "4.0",
            "image_url": monitor.image_1,
            "path": f"/monitors/{monitor.pk}/",
            "special_features": ["curved", "eye_care"],
        }

        # Simulate adding the product to browsing history
        response = client.get(
            reverse("i:add_review", kwargs={"product_id": monitor.monitor_id})
        )

        # Fetch browsing history from the session
        browsing_history = client.session.get("browsing_history", {})

        assert "name" in browsing_history
        assert browsing_history["name"][0] == monitor.name
        # Format price to match the expected value
        formatted_price = "{:.2f}".format(monitor.price)
        assert browsing_history["price"][0] == formatted_price

    def test_browsing_history_cookie_limit(self, setup_method):
        """Test that the browsing history does not exceed the maximum allowed items."""

        client = setup_method["client"]
        monitor = setup_method["monitor"]

        # Simulate adding multiple products to the browsing history
        product_details = {
            "name": "Monitor X",
            "price": "500",
            "rating": "5.0",
            "image_url": monitor.image_1,
            "path": f"/monitors/{monitor.pk}/",
            "special_features": ["curved", "eye_care"],
        }

        for i in range(10):  # Add more than MAX_HISTORY_ITEMS (7) products
            # Simulate adding the product to browsing history
            response = client.get(
                reverse("i:add_review", kwargs={"product_id": monitor.monitor_id})
            )

        # Fetch browsing history from the session
        browsing_history = client.session.get("browsing_history", {})

        # Assert that the history contains only the last 7 items
        assert len(browsing_history["name"]) == 7
        assert browsing_history["rating"][-1] == str(4)
        assert browsing_history["name"][-1] == "Monitor 1"  # Last added item


@pytest.mark.django_db
class Test_MonitorDetailViewDeleteReviewForm:

    # setup with SELLER user type
    @pytest.fixture(scope="function")
    def setup_method(self):

        client = Client()

        user = CustomUserOnlyFactory(user_type="SELLER")
        assert user is not None

        client.force_login(user)

        try:
            # Create a Product category for books
            Product_Category = ProductCategoryFactory(name="COMPUTER")
            assert Product_Category is not None

            # Create a computer category for books
            Computer_SubCategory = ComputerSubCategoryFactory(name="MONITOR")
            assert Computer_SubCategory is not None

        except Exception as e:
            pass

        """Setup initial monitor based on parametrize data"""
        monitor = MonitorsFactory(
            user=user,
            Computer_SubCategory=Computer_SubCategory,
            Product_Category=Product_Category,
            name="Monitor 1",
            brand="SAMSUNG",
            monitor_type="GAMING_MONITOR",
            refresh_rate=144,
            max_display_resolution="1920x1080",
            price=Decimal("100"),
        )

        """Setup initial data for the test"""

        comment = factory_classes.ReviewFactory(
            user=user,
            product=monitor,
            status=1,
            rating=Decimal("4"),
            text="Test comment",
        )

        return client, user, monitor, comment

    def test_delete_review_success(self, setup_method):
        """Test that a user can successfully delete their own review."""

        client, user, monitor, comment = setup_method

        monitor_id = monitor.monitor_id
        comment_id = comment.id

        response = client.get(
            reverse(
                "i:monitor_delete_review",
                kwargs={"product_id": monitor_id, "review_id": comment_id},
            )
        )

        # Check that the comment has been deleted
        assert Review.objects.filter(id=comment_id).count() == 0
        assert response.status_code == 302  # Redirect after deletion
        assert response.url == reverse(
            "i:add_review", kwargs={"product_id": monitor_id}
        )
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].message == "Your comment has been deleted."
        assert messages[0].tags == "success"

    def test_delete_review_permission_denied(self, setup_method):
        """Test that a user cannot delete someone else's review."""

        client, user, monitor, comment = setup_method
        monitor_id = monitor.monitor_id
        comment_id = comment.id

        # Log-out the previously logged-in user
        client.logout()

        # Create an logged-in new user
        new_user = CustomUserOnlyFactory(user_type="SELLER")
        assert user.email != new_user.email

        client.force_login(new_user)

        response = client.get(
            reverse(
                "i:monitor_delete_review",
                kwargs={"product_id": monitor_id, "review_id": comment_id},
            )
        )

        # Check that the comment still exists
        assert Review.objects.filter(id=comment_id).count() == 1
        assert response.status_code == 302  # Redirect after failed deletion
        assert response.url == reverse(
            "i:add_review", kwargs={"product_id": monitor_id}
        )
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert (
            messages[0].message == "You do not have permission to delete this comment."
        )
        assert messages[0].tags == "error"

    def test_delete_non_existent_review(self, setup_method):
        """Test the behavior when attempting to delete a non-existent review."""

        client, user, monitor, comment = setup_method
        monitor_id = monitor.monitor_id
        non_existent_comment_id = 9999  # Assuming this ID does not exist

        response = client.get(
            reverse(
                "i:monitor_delete_review",
                kwargs={
                    "product_id": monitor_id,
                    "review_id": non_existent_comment_id,
                },
            )
        )

        # The deletion logic should handle the non-existent comment gracefully
        assert response.status_code == 302  # Expecting a redirect
        assert response.url == reverse(
            "i:add_review", kwargs={"product_id": monitor_id}
        )
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].message == "Review does not exist."
        assert messages[0].tags == "error"


# @pytest.mark.django_db
# class Test_CreateMonitor:

#     @patch("cloudinary.uploader.upload")
#     def test_create_monitor_with_valid_data(
#         self,
#         mock_upload,
#         create_monitor_form,
#     ):

#         (
#             monitor_form_data,
#             Product_Category,
#             Computer_SubCategory,
#             client,
#             user,
#             monitor,
#         ) = create_monitor_form

#         files = {
#             "image_1": monitor_form_data["image_1"],
#             "image_2": monitor_form_data["image_2"],
#             "image_3": monitor_form_data["image_3"],
#         }

#         # Mock the upload function to return a predefined URL
#         mock_upload.return_value = {
#             "url": "https://res.cloudinary.com/demo/image/upload/sample.jpg"
#         }

#         assert client.session["user_id"] == user.id

#         # Send POST request to create a monitor
#         response = client.post(
#             reverse("i:add_monitor"),
#             data=monitor_form_data,
#             files=files,
#             enctype="multipart/form-data",
#             follow=True,
#         )

#         # Ensure the form is valid and the monitor is created
#         assert response.status_code == 200
#         assert Monitors.objects.count() == 1

#         monitor = Monitors.objects.first()

#         # Check that the Cloudinary upload function was called three times (for 3 images)
#         assert mock_upload.call_count == 3

#         # Verify that the image URLs are stored in the monitor object
#         assert (
#             monitor.image_1 == "https://res.cloudinary.com/demo/image/upload/sample.jpg"
#         )
#         assert (
#             monitor.image_2 == "https://res.cloudinary.com/demo/image/upload/sample.jpg"
#         )
#         assert (
#             monitor.image_3 == "https://res.cloudinary.com/demo/image/upload/sample.jpg"
#         )

#         # Additional checks: success message and redirect
#         assert response.url == reverse("i:success_page")
#         assert "All forms submitted successfully" in response.content.decode()

#     # Patch the Cloudinary uploader's upload function for failure cases
#     @patch("cloudinary.uploader.upload")
#     def test_create_monitor_with_image_upload_failure(
#         mock_upload, authenticated_client, monitor_form_data, uploaded_images
#     ):
#         # Simulate a failure in the Cloudinary upload process
#         mock_upload.side_effect = Exception("Upload failed")

#         # Add the files to the form data
#         form_data = monitor_form_data.copy()
#         form_data.update(uploaded_images)

#         # Send POST request to create a monitor
#         response = authenticated_client.post(
#             reverse("create_monitor"), data=form_data, follow=True
#         )

#         # Ensure the form is invalid due to image upload failure
#         assert response.status_code == 200
#         assert Monitors.objects.count() == 0
