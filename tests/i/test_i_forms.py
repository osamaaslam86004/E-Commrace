import pytest
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from i.models import ProductCategory, ComputerSubCategory, Monitors, Special_Features
from i.forms import (
    ProductCategoryForm,
    ComputerSubCategoryForm,
    MonitorsForm,
    ReviewForm,
)
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i.factory_classes import (
    MonitorsFactory,
    ProductCategoryFactory,
    ComputerSubCategoryFactory,
)
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


@pytest.fixture
def product_category():
    return ProductCategory.objects.create(name="COMPUTER")


@pytest.fixture
def computer_subcategory(product_category):
    return ComputerSubCategory.objects.create(
        name="MONITORS", product_category=product_category
    )


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
    print(f"Uploaded file size: {len(uploaded_file)} bytes")

    return uploaded_file


@pytest.fixture
def create_product():
    def _create_product(user_type, product_category_name, computer_sub_category_name):
        # create the user
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
def Review_form_data(create_image):
    def _Review_form_data():
        form_data = {
            "rating": "4.5",  # Example rating value
            "image_1": create_image,
            "image_2": create_image,
            "text": "This is a test review.",
        }

        files = {"image_1": create_image, "image_2": create_image}
        # files["image_1"].seek(0)  # Seek to the beginning of file content
        # files["image_2"].seek(0)  # Seek to the beginning of file content

        assert len(files["image_1"]) > 0 and len(files["image_2"]) > 0

        form = ReviewForm(data=form_data, files=files)
        assert form.is_valid()

        form.is_valid()

        return form, files

    return _Review_form_data


@pytest.mark.django_db
class Test_ProductCategoryForm:

    @pytest.mark.parametrize(
        "name, is_valid",
        [
            ("COMPUTER", True),
            ("ELECTRONICS", True),
            ("BOOKS", True),
            ("Invalid", False),
        ],
    )
    def test_product_category_form_choices(self, name, is_valid):
        form_data = {"name": name}
        form = ProductCategoryForm(data=form_data)
        assert form.is_valid() == is_valid

    @pytest.mark.parametrize(
        "name",
        [("COMPUTER"), ("ELECTRONICS"), ("BOOKS")],
    )
    def test_product_category_form_save(self, name):
        form_data = {"name": name}
        form = ProductCategoryForm(data=form_data)
        assert form.is_valid()
        category = form.save()
        assert isinstance(category, ProductCategory)
        assert category.name == form_data["name"]


@pytest.mark.django_db
class Test_ComputerSubCategoryForm:

    @pytest.mark.parametrize(
        "name, is_valid",
        [
            ("LAPTOP_ACCESSORIES", True),
            ("COMPUTERS_AND_TABLETS", True),
            ("TABLETS_REPLACEMENT_PARTS", True),
            ("SERVERS", True),
            ("MONITORS", True),
            ("INVALID_SUBCATEGORY", False),
        ],
    )
    def test_computer_subcategory_form_choices(self, name, is_valid):
        # CREATING PRODUCT CATEGORY
        ProductCategory.objects.create(name="COMPUTER"),
        form_data = {"name": name}
        form = ComputerSubCategoryForm(data=form_data)
        assert form.is_valid() == is_valid

    @pytest.mark.parametrize(
        "sub_category_name",
        [
            ("LAPTOP_ACCESSORIES"),
            ("COMPUTERS_AND_TABLETS"),
            ("TABLETS_REPLACEMENT_PARTS"),
            ("SERVERS"),
            ("MONITORS"),
        ],
    )
    def test_computer_subcategory_form_save(self, sub_category_name):
        # create Product Category
        category = ProductCategory.objects.create(name="COMPUTER")

        # checking Form validation
        form_data = {"name": sub_category_name}
        form = ComputerSubCategoryForm(data=form_data)
        assert form.is_valid()

        # saving the form, and bind it to 'COMPUTER' ProductCategory
        subcategory = form.save(commit=False)
        subcategory.product_category = category
        subcategory.save()

        # Assertions
        assert isinstance(subcategory, ComputerSubCategory)
        assert subcategory.name == form_data["name"]
        assert subcategory.product_category == category


@pytest.mark.django_db
class Test_MonitorForm:

    @pytest.mark.parametrize(
        "monitor_form_data, is_valid",
        [
            (
                {
                    "name": "name",
                    "image_1": None,
                    "image_2": None,
                    "image_3": None,
                    "is_active": True,
                    "brand": "LG",
                    "aspect_ratio": "16:9",
                    "max_display_resolution": "1280x1024",
                    "screen_size": "27 inch",
                    "monitor_type": "GAMING_MONITOR",
                    "refresh_rate": 240,
                    "mounting_type": "WALL_MOUNT",
                    "item_dimensions": "111 x 111 x 111",
                    "item_weight": 1,
                    "voltage": 240,
                    "color": "Black",
                    "hdmi_port": 2.0,
                    "built_speakers": "Yes",
                    "price": 55.5,
                    "quantity_available": 144,
                    "choose_special_features": ["Frameless"],
                },
                True,
            ),
            (
                {
                    "name": "name",
                    "image_1": None,
                    "image_2": None,
                    "image_3": None,
                    "is_active": True,
                    "brand": "ASUS",
                    "aspect_ratio": "16:9",
                    "max_display_resolution": "1280x1024",
                    "screen_size": "21 inch",
                    "monitor_type": "GAMING_MONITOR",
                    "refresh_rate": "240 Hz",
                    "mounting_type": "Invalid",  # form not valid
                    "item_dimensions": "111 x 111 x 111",
                    "item_weight": "11 lb",
                    "voltage": "24 V",
                    "color": "Read",
                    "hdmi_port": 1.0,
                    "built_speakers": "Yes",
                    "price": 550.5,
                    "quantity_available": 1440,
                    "choose_special_features": ["Flicker-Free"],
                },
                False,
            ),
        ],
    )
    def test_monitors_form_validation(
        self,
        create_image,
        monitor_form_data,
        is_valid,
    ):
        Special_Features.objects.create(name="Frameless"),
        Special_Features.objects.create(name="Flicker-Free"),

        # getting the ids of special features
        special_features_objs = Special_Features.objects.filter(
            name__in=monitor_form_data["choose_special_features"]
        )

        monitor_form_data["choose_special_features"] = list(
            special_features_objs.values_list("id", flat=True)
        )

        files = {}
        files["image_1"] = create_image
        files["image_2"] = create_image
        files["image_3"] = create_image

        form = MonitorsForm(data=monitor_form_data, files=files)
        assert form.is_valid() == is_valid

    @pytest.mark.parametrize(
        "monitor_form_data",
        [
            {
                "name": "name",
                "image_1": None,
                "image_2": None,
                "image_3": None,
                "is_active": True,
                "brand": "LG",
                "aspect_ratio": "16:9",
                "max_display_resolution": "1280x1024",
                "screen_size": "27 inch",
                "monitor_type": "GAMING_MONITOR",
                "refresh_rate": 240,
                "mounting_type": "WALL_MOUNT",
                "item_dimensions": "111 x 111 x 111",
                "item_weight": 1,
                "voltage": 240,
                "color": "Black",
                "hdmi_port": 2.0,
                "built_speakers": "Yes",
                "price": 55.5,
                "quantity_available": 144,
                "choose_special_features": ["Frameless"],
            },
        ],
    )
    def test_monitors_form(
        self, create_image, monitor_form_data, product_category, computer_subcategory
    ):
        Special_Features.objects.create(name="Frameless"),

        # getting the ids of special features
        special_features_objs = Special_Features.objects.filter(
            name__in=monitor_form_data["choose_special_features"]
        )

        monitor_form_data["choose_special_features"] = list(
            special_features_objs.values_list("id", flat=True)
        )

        files = {}
        files["image_1"] = create_image
        files["image_2"] = create_image
        files["image_3"] = create_image

        assert files["image_1"] is not None
        assert files["image_2"] is not None
        assert files["image_3"] is not None

        form = MonitorsForm(data=monitor_form_data, files=files)
        assert form.is_valid()

        monitor = form.save(commit=False)

        # creating the user
        user = CustomUserOnlyFactory(user_type="SELLER")

        # binding the monitor instance to Productcategory, and computerSubcategory
        monitor.Product_Category = product_category
        monitor.Computer_SubCategory = computer_subcategory
        monitor.user = user

        for key, image_file in files.items():
            setattr(monitor, f"image_{key[-1]}", image_file)
        monitor.save()

        # Assertions
        assert isinstance(monitor, Monitors)
        assert monitor.monitor_type == monitor_form_data["monitor_type"]
        assert monitor.mounting_type == monitor_form_data["mounting_type"]
        assert (
            monitor.max_display_resolution
            == monitor_form_data["max_display_resolution"]
        )
        assert monitor.refresh_rate == monitor_form_data["refresh_rate"]
        assert monitor.brand == monitor_form_data["brand"]
        assert monitor.is_active == monitor_form_data["is_active"]
        assert monitor.Product_Category == product_category
        assert monitor.Computer_SubCategory == computer_subcategory


@pytest.mark.django_db
class Test_ReviewForm:

    def test_review_form_valid(self, create_image):

        form_data = {
            "rating": "4.5",  # Example rating value
            "image_1": None,
            "image_2": None,
            "text": "This is a test review.",
        }

        files = {"image_1": create_image, "image_2": create_image}

        form = ReviewForm(data=form_data, files=files)
        assert form.is_valid()

    def test_review_form_invalid(self):

        form_data = {
            "rating": "invalid_rating",  # Invalid rating value
            "text": "This is a test review.",
            "image_2": None,
            "image_1": None,
        }

        form = ReviewForm(data=form_data)
        assert not form.is_valid()
        assert "rating" in form.errors

    def test_form_save(self, create_product, Review_form_data, create_image):
        # create product_category, and computer sub category
        user, product_category, computer_sub_category = create_product(
            "SELLER", "COMPUTER", "MONITOR"
        )
        # Create the Monitor
        monitor = MonitorsFactory(
            user=user,
            Product_Category=product_category,
            Computer_SubCategory=computer_sub_category,
        )

        # creating form data and image files
        form, files = Review_form_data()

        review = form.save(commit=False)
        review.user = user
        review.product = monitor

        # binding image files with Review instance
        for key, image_file in files.items():
            setattr(review, f"image_{key[-1]}", image_file)

        # review.image_1 = "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"
        # review.image_2 = "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"
        # review.image_3 = "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"

        assert review.image_1 == files["image_1"]
        assert review.image_2 == files["image_2"]

        try:
            instance = review.save()  # =====> this will raise Empty File error
        except Exception as e:
            print(f"exception printed-------------{e}")

        # assert (
        #     instance.image_1
        #     == "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"
        # )
        assert instance.image == files["image_1"]
        assert instance.rating == float(Review_form_data["rating"])
        assert instance.text == Review_form_data["text"]
