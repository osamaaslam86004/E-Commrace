# test_models.py
import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from i.models import (
    ProductCategory,
    ComputerSubCategory,
    Special_Features,
    Monitors,
    Review,
)
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i.factory_classes import (
    SpecialFeaturesFactory,
    MonitorsFactory,
    ComputerSubCategoryFactory,
    ProductCategoryFactory,
    ReviewFactory,
)
import random
from faker import Faker
import logging

faker = Faker()
# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)


CustomUser = get_user_model()


@pytest.fixture
def user_factory():
    def _user_factory(user_type):
        return CustomUserOnlyFactory(user_type=user_type)

    return _user_factory


@pytest.fixture
def sample_special_feature():
    feature_names = random.sample(
        [choice[0] for choice in Special_Features.SPECIAL_FEATURES_CHOICES], 2
    )
    features = [Special_Features.objects.create(name=name) for name in feature_names]
    return feature_names, features


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
def build_setup_testing_Review(create_product, sample_special_feature):

    def _build_setup_testing_Review(user_type, product_category, computer_sub_category):
        # build setup for category and user
        user, product_category, computer_sub_category = create_product(
            user_type, product_category, computer_sub_category
        )
        # create the special features
        feature_names, features = sample_special_feature
        # Create the Monitor
        monitor1 = MonitorsFactory(
            user=user,
            special_features=features,
            Product_Category=product_category,
            Computer_SubCategory=computer_sub_category,
        )
        return user, product_category, computer_sub_category, monitor1

    return _build_setup_testing_Review


@pytest.mark.django_db
class Test_Categories:

    @pytest.mark.parametrize(
        "product_category_type_choices", ["COMPUTER", "ELECTRONICS", "BOOKS"]
    )
    def test_product_category_creation(self, product_category_type_choices):
        category = ProductCategoryFactory(name=product_category_type_choices)

        assert len(ProductCategory.objects.all()) == 1

        assert ProductCategory.objects.get(name=category.name)

    def test_product_category_choices(self):
        invalid_category = ProductCategoryFactory(name="Invalid Category")
        with pytest.raises(ValidationError):
            invalid_category.full_clean()

    @pytest.mark.parametrize(
        "product_sub_category_type_choices",
        [
            "LAPTOP_ACCESSORIES",
            "COMPUTERS_AND_TABLETS",
            "TABLETS_REPLACEMENT_PARTS",
            "SERVERS",
            "MONITORS",
        ],
    )
    def test_computer_subcategory_creation(self, product_sub_category_type_choices):
        category = ProductCategoryFactory(name="COMPUTER")
        subcategory = ComputerSubCategoryFactory(
            name=product_sub_category_type_choices, product_category=category
        )

        assert subcategory.product_category == category
        assert len(ComputerSubCategory.objects.all()) == 1


@pytest.mark.django_db
class Test_Monitors:
    def test_create_monitor(self, create_product):
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

        # get the monitor from database
        instance_db = Monitors.objects.get(monitor_id=monitor.monitor_id)
        assert monitor.name == instance_db.name
        assert monitor.user == instance_db.user
        assert monitor.Product_Category == instance_db.Product_Category
        assert monitor.Computer_SubCategory == instance_db.Computer_SubCategory
        assert monitor.special_features.count() == 3
        assert list(monitor.special_features.values_list("name", flat=True)) == list(
            instance_db.special_features.values_list("name", flat=True)
        )

    def test_monitor_validation_Computer_SubCategory(self):
        # Test validation errors
        user = CustomUserOnlyFactory()
        # creating the product category
        product_category = ProductCategoryFactory(name="COMPUTER")

        with pytest.raises(IntegrityError):
            # Missing required fields
            MonitorsFactory(
                user=user,
                Product_Category=product_category,
                Computer_SubCategory=None,
            )

    def test_monitor_validation_price_value(self, create_product):
        # create product_category, and computer sub category
        user, product_category, computer_sub_category = create_product(
            "SELLER", "COMPUTER", "MONITOR"
        )
        with pytest.raises(ValidationError):
            # Invalid price
            monitor = MonitorsFactory(
                user=user,
                Product_Category=product_category,
                Computer_SubCategory=computer_sub_category,
                price=0.99,
            )
            monitor.full_clean()  # this will trigger the validation

    def test_monitor_integrity_error(self, create_product):
        # create product_category, and computer sub category
        user, product_category, computer_sub_category = create_product(
            "SELLER", "COMPUTER", "MONITOR"
        )

        # creating instance for monitor
        monitor = MonitorsFactory(
            user=user,
            Product_Category=product_category,
            Computer_SubCategory=computer_sub_category,
        )

        with pytest.raises(IntegrityError):
            # Unique constraint violation (monitor_id is AutoField and primary key)
            Monitors.objects.create(
                monitor_id=monitor.monitor_id,
                user=user,
                Product_Category=product_category,
                Computer_SubCategory=computer_sub_category,
            )

    def test_deletion_cascade(self, build_setup_testing_Review):
        # create a monitor product
        user, product_category, computer_sub_category, monitor1 = (
            build_setup_testing_Review("SELLER", "COMPUTER", "MONITOR")
        )

        # deleting the 'seller' type user will delete all of his/her products
        monitor1.user.delete()
        assert not CustomUser.objects.filter(id=user.id).exists()
        assert not Monitors.objects.filter(monitor_id=monitor1.monitor_id).exists()


@pytest.mark.django_db
class Test_SpecialFeatures:
    def test_special_feature_creation(self):
        # Create a special feature using the factory
        special_feature = SpecialFeaturesFactory()
        assert special_feature.name in dict(Special_Features.SPECIAL_FEATURES_CHOICES)

    def test_special_feature_unique_name(self):
        # Create a special feature
        special_feature = SpecialFeaturesFactory(name="adaptive_sync")
        assert special_feature.name == "adaptive_sync"

        # Attempt to create another special feature with the same name
        with pytest.raises(ValidationError):
            special_feature_duplicate = Special_Features(name="adaptive_sync")
            special_feature_duplicate.full_clean()  # This triggers the validation
            special_feature_duplicate.save()

    def test_special_feature_string_representation(self):
        # Create a special feature
        special_feature = SpecialFeaturesFactory(name="blue_light_filter")
        assert str(special_feature) == "Blue Light Filter"

    def test_special_feature_default_value(self):
        # Create a special feature with default value
        special_feature = Special_Features()
        assert special_feature.name == "Frameless"

    def test_special_feature_choices(self):
        # Ensure all choices are valid
        for choice, _ in Special_Features.SPECIAL_FEATURES_CHOICES:
            special_feature = Special_Features(name=choice)
            special_feature.full_clean()  # This should not raise any validation errors

    def test_reverse_many_to_many_relation(self, create_product):
        # Create special features
        feature1 = SpecialFeaturesFactory(name="adaptive_sync")
        feature2 = SpecialFeaturesFactory(name="blue_light_filter")

        # create product_category, and computer sub category
        user, product_category, computer_sub_category = create_product(
            "SELLER", "COMPUTER", "MONITOR"
        )
        # Create the Monitor
        monitor1 = MonitorsFactory(
            user=user,
            special_features=[feature1, feature2],
            Product_Category=product_category,
            Computer_SubCategory=computer_sub_category,
        )
        assert monitor1 is not None
        assert monitor1.Computer_SubCategory.name == "MONITOR"

        # Create the Monitor
        monitor2 = MonitorsFactory(
            user=user,
            special_features=[feature1],
            Product_Category=product_category,
            Computer_SubCategory=computer_sub_category,
        )
        assert monitor2 is not None
        assert monitor2.Computer_SubCategory.name == "MONITOR"

        # Check the relation from the monitor side
        assert feature1 in monitor1.special_features.all()
        assert feature2 in monitor1.special_features.all()
        assert feature1 in monitor2.special_features.all()
        assert feature2 not in monitor2.special_features.all()

        # Check the reverse relation from the special features side
        assert monitor1 in feature1.monitors_set.all()
        assert monitor2 in feature1.monitors_set.all()
        assert monitor1 in feature2.monitors_set.all()
        assert monitor2 not in feature2.monitors_set.all()


@pytest.mark.django_db
class Test_ReviewModel:

    def test_review_creation(self):
        review = ReviewFactory()
        assert review.id is not None
        assert isinstance(review, Review)

    def test_review_default_status(self):
        review = ReviewFactory()
        assert review.status == True

    def test_review_rating_limits(self, build_setup_testing_Review):
        # create a monitor product
        user, product_category, computer_sub_category, monitor1 = (
            build_setup_testing_Review("SELLER", "COMPUTER", "MONITOR")
        )
        review = ReviewFactory(user=user, product=monitor1, rating=4.5)
        assert review.rating == 4.5

        # inserting invalid value for 'rating', model will not raise validation error
        review = ReviewFactory(user=user, product=monitor1, rating=6.0)
        review.full_clean()

    def test_review_relationships(self, build_setup_testing_Review):
        # create a monitor product
        user, product_category, computer_sub_category, monitor1 = (
            build_setup_testing_Review("SELLER", "COMPUTER", "MONITOR")
        )

        assert monitor1 is not None
        assert monitor1.Computer_SubCategory.name == "MONITOR"

        # return user, product_category, computer_sub_category
        review = ReviewFactory(user=user, product=monitor1)
        assert isinstance(review.user, CustomUser)
        assert isinstance(review.product, Monitors)
        assert review.user.id is not None
        assert review.product.monitor_id is not None
        assert review.user.username == user.username
        assert review.product.name == monitor1.name

    def test_review_str(self):
        review = ReviewFactory()
        assert str(review) == f"{review.user.username} - {review.product.name} Review"

    def test_review_image_defaults(self):
        review = ReviewFactory()
        assert (
            review.image_1
            == "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"
        )
        assert (
            review.image_2
            == "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"
        )

    def test_review_deletion_cascade(self, build_setup_testing_Review):
        # create a monitor product
        user, product_category, computer_sub_category, monitor1 = (
            build_setup_testing_Review("SELLER", "COMPUTER", "MONITOR")
        )
        review = ReviewFactory(user=user, product=monitor1)

        review.user.delete()
        assert not Review.objects.filter(id=review.id).exists()

        # Ensure that deleting the product also deletes the review
        monitor1.delete()
        assert not Review.objects.filter(id=review.id).exists()
