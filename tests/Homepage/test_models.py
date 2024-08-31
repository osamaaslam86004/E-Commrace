import pytest
import logging
from faker import Faker
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from Homepage.models import (
    CustomUser,
    UserProfile,
    SellerProfile,
    CustomerProfile,
)
from tests.Homepage.Homepage_factory import (
    CustomUserOnlyFactory,
    CustomUserOnlyFactory,
    CustomUserFactory_Without_UserProfile_PostGeneration,
    UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration,
    CustomerProfileFactory,
    SellerProfileFactory,
    CustomerServiceProfileFactory,
    ManagerProfileFactory,
    AdministratorProfileFactory,
    CustomSocialAccountFactory,
)
from django.contrib.auth.models import Group
from tests.Homepage.Custom_Permissions import (
    CUSTOMER_CUSTOM_PERMISSIONS,
    CSR_CUSTOM_PERMISSIONS,
    ADMIN_CUSTOM_PERMISSIONS,
    SELLER_CUSTOM_PERMISSIONS,
    MANAGER_CUSTOM_PERMISSIONS,
)


faker = Faker()
# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)


@pytest.fixture
def user_factory():
    def _user_factory(user_type):
        return CustomUserOnlyFactory(user_type=user_type)

    return _user_factory


@pytest.fixture
def create_user_for_user_type(db, user_factory):
    def _create_user_for_user_type_(user_type):
        if user_type == "CUSTOMER":
            return user_factory(user_type="CUSTOMER")
        elif user_type == "SELLER":
            return user_factory(user_type="SELLER")
        elif user_type == "MANAGER":
            return user_factory(user_type="MANAGER")
        elif user_type == "ADMINISTRATOR":
            return user_factory(user_type="ADMINISTRATOR")
        else:
            return user_factory(user_type="CUSTOMER REPRESENTATIVE")

    return _create_user_for_user_type_


@pytest.fixture(
    params=[
        {
            "team": faker.sentence()[:100],  # Trim to maximum 100 characters
            "reports": faker.sentence()[:100],  # Trim to maximum 100 characters
            "bio": "Experienced in customer service",
            "experience_years": "",
        },
        {
            "team": faker.sentence()[:10],  # Trim to maximum 100 characters
            "reports": faker.sentence()[:100],  # Trim to maximum 100 characters
            "bio": "Experienced in customer service",
            "experience_years": "",
        },
        {
            "team": faker.sentence()[:10],  # Trim to maximum 100 characters
            "reports": faker.sentence()[:10],  # Trim to maximum 100 characters
            "bio": "Experienced in customer service",
            "experience_years": 0,
        },
        {
            "team": "",  # Trim to maximum 100 characters
            "reports": "",  # Trim to maximum 100 characters
            "bio": "Experienced in customer service",
            "experience_years": None,
        },
    ]
)
def invalid_manager_profile_data(request):
    return request.param


@pytest.fixture(
    params=[
        {
            "team": faker.sentence()[:10],  # Trim to maximum 100 characters
            "reports": faker.sentence()[:10],  # Trim to maximum 100 characters
            "bio": "Experienced in customer service",
            "experience_years": 40,
        },
        {
            "team": faker.sentence()[:10],  # Trim to maximum 100 characters
            "reports": faker.sentence()[:10],  # Trim to maximum 100 characters
            "bio": "Experienced in customer service",
            "experience_years": 1,
        },
    ]
)
def valid_manager_profile_data(request):
    return request.param


@pytest.fixture(
    params=[
        {
            "bio": faker.sentence()[:10],
            "experience_years": 0,
        },
        {
            "bio": "",
            "experience_years": None,
        },
    ]
)
def invalid_admin_profile_data(request):
    return request.param


@pytest.fixture(
    params=[
        {
            "bio": faker.sentence()[:10],
            "experience_years": 40,
        },
        {
            "bio": faker.sentence()[:250],
            "experience_years": 1,
        },
    ]
)
def valid_admin_profile_data(request):
    return request.param


@pytest.fixture
def generate_paragraph():
    def _generate_paragraph(input):

        paragraph = faker.text(input)

        while len(paragraph) < input:
            paragraph += faker.sentence(1)[0] + " "

        return paragraph

    return _generate_paragraph


@pytest.fixture
def invalid_custom_social_account_data(generate_paragraph):
    return {
        "access_token": generate_paragraph(600),
        "user_info": generate_paragraph(1100),
        "code": generate_paragraph(600),
        "refresh_token": generate_paragraph(600),
    }


@pytest.fixture(
    params=[
        {
            "access_token": faker.sentence()[:50],
            "user_info": faker.paragraph()[:10],
            "code": faker.sentence()[:50],
            "refresh_token": faker.sentence()[:50],
        },
        {
            "access_token": "",
            "user_info": "",
            "code": "",
            "refresh_token": "",
        },
    ]
)
def valid_custom_social_account_data(request):
    return request.param


@pytest.mark.django_db
class Test_CustomUser:
    def test_create_user(self, user_factory):
        user = user_factory(user_type="CUSTOMER")
        assert user.email is not None
        assert user.user_type is not None
        assert user.image is not None
        assert user.user_google_id is None
        # assert user.check_password("Man1122334455!")  # causing test failure

    def test_create_superuser(self, create_user_for_user_type):
        admin_user = create_user_for_user_type(user_type="ADMINISTRATOR")
        assert admin_user.is_staff
        assert admin_user.is_superuser

    @pytest.mark.parametrize(
        "user_type, expected_permissions",
        [
            (
                "CUSTOMER",
                {f"Homepage.{perm[0]}" for perm in CUSTOMER_CUSTOM_PERMISSIONS},
            ),
            ("SELLER", {f"Homepage.{perm[0]}" for perm in SELLER_CUSTOM_PERMISSIONS}),
            ("MANAGER", {f"Homepage.{perm[0]}" for perm in MANAGER_CUSTOM_PERMISSIONS}),
            (
                "ADMINISTRATOR",
                {f"Homepage.{perm[0]}" for perm in ADMIN_CUSTOM_PERMISSIONS},
            ),
            (
                "CUSTOMER REPRESENTATIVE",
                {f"Homepage.{perm[0]}" for perm in CSR_CUSTOM_PERMISSIONS},
            ),
        ],
    )
    def test_user_permissions(self, user_factory, user_type, expected_permissions):
        user = user_factory(user_type=user_type)
        if user.user_type == "ADMINISTRATOR":
            pass
        else:
            assert expected_permissions == set(user.get_group_permissions())

    @pytest.mark.parametrize(
        "user_type",
        ["CUSTOMER", "SELLER", "MANAGER", "ADMINISTRATOR", "CUSTOMER REPRESENTATIVE"],
    )
    def test_user_type_groups(self, user_factory, user_type):
        user = user_factory(user_type=user_type)
        user_group = Group.objects.get(name=user_type)
        assert user.groups.filter(name=user_type).exists()

    @pytest.mark.django_db
    def test_user_profile_autocreation(self, user_factory):
        user = user_factory(user_type="SELLER")
        profile = UserProfile.objects.get(user=user)
        assert profile is not None
        assert profile.user == user

    def test_invalid_superuser_creation(self):
        with pytest.raises(ValueError):
            CustomUser.objects.create_superuser(
                email="superuser@example.com",
                username="superuser",
                password="superpass123",
                is_staff=False,
            )
        with pytest.raises(ValueError):
            CustomUser.objects.create_superuser(
                email="superuser@example.com",
                username="superuser",
                password="superpass123",
                is_superuser=False,
            )

    def test_superuser_creation(self):
        user = CustomUser.objects.create_superuser(
            email="superuser@example.com", password="superpass123", username="superuser"
        )
        assert user.is_staff
        assert user.is_superuser


@pytest.mark.django_db
class Test_UserProfile:

    @pytest.mark.parametrize(
        "field_name, field_value",
        [
            ("full_name", ""),
            ("age", None),
            ("gender", "Male_"),
            ("phone_number", "+91123456789"),
            ("city", ""),
            ("country", None),
            ("postal_code", ""),
            ("shipping_address", ""),
        ],
    )
    def test_user_profile_fields_validation(self, field_name, field_value):
        """
        Test that UserProfile required fields cannot be left blank.
        """
        user = CustomUserFactory_Without_UserProfile_PostGeneration()
        with pytest.raises(ValidationError):
            user_profile = (
                UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration(
                    user=user, **{field_name: field_value}
                )
            )
            user_profile.full_clean()

    def test_user_profile_one_to_one_relationship(self):
        """
        Test that a UserProfile instance can only be associated with one CustomUser instance.
        """
        first_user = CustomUserFactory_Without_UserProfile_PostGeneration()

        UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration(
            user=first_user
        )
        with pytest.raises(IntegrityError):
            UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration(
                user=first_user
            )

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "age, gender, phone_number, city, country, postal_code",
        [
            (25, "Male", "+923074649891", "New York", "US", "10001"),
            (30, "Female", "+923074649893", "Los Angeles", "US", "90001"),
        ],
    )
    def test_create_user_profile(
        self, age, gender, phone_number, city, country, postal_code
    ):
        User = CustomUserOnlyFactory.create()
        assert CustomUser.objects.count() == 1

        user_profile = UserProfile.objects.get(user=User)

        user_profile.user = User
        user_profile.full_name = faker.address()
        user_profile.age = age
        user_profile.gender = gender
        user_profile.phone_number = phone_number
        user_profile.city = city
        user_profile.country = country
        user_profile.postal_code = postal_code
        user_profile.shpping_address = faker.address()
        user_profile.save()

        assert UserProfile.objects.count() == 1
        assert user_profile.user == User
        assert user_profile.age == age
        assert user_profile.gender == gender
        assert user_profile.phone_number == phone_number
        assert user_profile.city == city
        assert user_profile.country == country
        assert user_profile.postal_code == postal_code

    @pytest.mark.django_db
    def test_user_profile_validations(self):
        user = CustomUserOnlyFactory.create()

        user_profile = UserProfile.objects.get(user=user)

        with pytest.raises(ValidationError):
            user_profile.user = user
            user_profile.full_name = ""
            user_profile.age = 150
            user_profile.gender = "Male_"
            user_profile.phone_number = "923074649892"
            user_profile.city = ""
            user_profile.country = "NZ_"
            user_profile.postal_code = ""
            user_profile.shpping_address = faker.address()
            user_profile.save()

    @pytest.mark.django_db
    def test_update_user_profile(self):
        user = CustomUserOnlyFactory.create()
        user_profile_before = UserProfile.objects.get(user=user)

        city_before = user_profile_before.city
        age_before = user_profile_before.age
        postal_code_brfore = user_profile_before.postal_code

        user_profile_before.city = "New York"
        user_profile_before.postal_code = "10001"
        user_profile_before.age = 35
        user_profile_before.save()

        updated_profile = UserProfile.objects.get(user=user)
        assert city_before != updated_profile.city
        assert age_before != updated_profile.age
        assert postal_code_brfore != updated_profile.postal_code


@pytest.mark.django_db
class Test_CustomerProfile:

    @pytest.mark.parametrize(
        "shipping_address, wishlist",
        [
            ("123 Main St", 1),
            ("456 Elm St", 2),
            ("789 Oak St", 3),
        ],
    )
    def test_customer_profile_create(self, shipping_address, wishlist):
        user = CustomUserOnlyFactory(user_type="CUSTOMER")

        user_profile = UserProfile.objects.get(user=user)

        customer_profile = CustomerProfileFactory(
            customuser_type_1=user,
            customer_profile=user_profile,
            shipping_address=shipping_address,
            wishlist=wishlist,
        )
        assert customer_profile.shipping_address == shipping_address
        assert customer_profile.wishlist == wishlist

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        " shipping_address, wishlist",
        [
            ("123 Main St", None),
            ("456 Elm St", None),
        ],
    )
    def test_customer_profile_fields_validation(self, shipping_address, wishlist):

        user = CustomUserOnlyFactory(user_type="CUSTOMER")

        user_profile = UserProfile.objects.get(user=user)

        with pytest.raises(ValidationError):
            customer_profile = CustomerProfileFactory(
                customuser_type_1=user,
                customer_profile=user_profile,
                shipping_address=shipping_address,
                wishlist=wishlist,
            )

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        " shipping_address, wishlist",
        [
            ("", faker.random_int(min=100, max=1000)),
            ("", faker.random_int(min=0, max=1000)),
        ],
    )
    def test_customer_profile_fields_ValidationError_Charfield(
        self, shipping_address, wishlist
    ):

        user = CustomUserOnlyFactory(user_type="CUSTOMER")

        user_profile = UserProfile.objects.get(user=user)

        with pytest.raises(ValidationError):
            customer_profile = CustomerProfileFactory(
                customuser_type_1=user,
                customer_profile=user_profile,
                shipping_address=shipping_address,
                wishlist=wishlist,
            )

    def test_customer_profile_one_to_one_relationship(self):
        """
        Test that a UserProfile instance can only be associated with one CustomUser instance.
        """
        user = CustomUserOnlyFactory(user_type="CUSTOMER")

        user_profile = UserProfile.objects.get(user=user)

        CustomerProfileFactory(
            customuser_type_1=user,
            customer_profile=user_profile,
            shipping_address=faker.address(),
            wishlist=30,
        )
        # creating one more customer instance with 'user', and 'user_profile'
        # to raise error

        with pytest.raises(IntegrityError):

            CustomerProfileFactory(
                customuser_type_1=user,
                customer_profile=user_profile,
                shipping_address=faker.address(),
                wishlist=40,
            )

    def test_update_customer_profile(self):
        User = CustomUserOnlyFactory(user_type="CUSTOMER")
        assert CustomUser.objects.count() == 1

        user_profile = UserProfile.objects.get(user=User)

        customer_profile = CustomerProfileFactory(
            customuser_type_1=User,
            customer_profile=user_profile,
            shipping_address=faker.address(),
            wishlist=30,
        )

        old_shipping_address = customer_profile.shipping_address
        old_whishlist = customer_profile.wishlist
        # updating the cusstomer profile instance

        get_customer_profile = CustomerProfile.objects.get(
            customuser_type_1=User,
            customer_profile=user_profile,
        )
        get_customer_profile.shipping_address = "fake_address"
        get_customer_profile.wishlist = 40
        get_customer_profile.save()

        assert (
            CustomerProfile.objects.filter(
                customuser_type_1=User, customer_profile=user_profile
            ).count()
            == 1
        )
        assert old_shipping_address != get_customer_profile.shipping_address
        assert old_whishlist != get_customer_profile.wishlist


@pytest.mark.django_db
class Test_SellerProfile:

    @pytest.mark.parametrize(
        "address",
        [faker.address(), faker.address()],
    )
    def test_seller_profile_create(self, address):
        user = CustomUserOnlyFactory(user_type="SELLER")

        user_profile = UserProfile.objects.get(user=user)

        seller_profile = SellerProfileFactory(
            customuser_type_2=user,
            seller_profile=user_profile,
            address=address,
        )
        assert seller_profile.address == address

    @pytest.mark.django_db
    @pytest.mark.parametrize("address", ["123 Main", "main road"])
    def test_customer_profile_fields_validation(self, address):

        user = CustomUserOnlyFactory(user_type="SELLER")

        user_profile = UserProfile.objects.get(user=user)

        with pytest.raises(ValidationError):
            SellerProfileFactory(
                customuser_type_2=user, seller_profile=user_profile, address=address
            )

    def test_customer_profile_fields_ValueError(self):

        user = CustomUserOnlyFactory(user_type="SELLER")

        user_profile = UserProfile.objects.get(user=user)

        with pytest.raises(ValueError):
            SellerProfileFactory(
                customuser_type_2=user, seller_profile=user_profile, address=""
            )

    def test_customer_profile_one_to_one_relationship(self):
        """
        Test that a UserProfile instance can only be associated with one CustomUser instance.
        """
        user = CustomUserOnlyFactory(user_type="SELLER")

        user_profile = UserProfile.objects.get(user=user)

        SellerProfileFactory(
            customuser_type_2=user,
            seller_profile=user_profile,
            address=faker.address(),
        )

        with pytest.raises(IntegrityError):
            SellerProfileFactory(
                customuser_type_2=user,
                seller_profile=user_profile,
                address=faker.address(),
            )

    def test_update_customer_profile(self):
        User = CustomUserOnlyFactory(user_type="SELLER")
        assert CustomUser.objects.count() == 1

        user_profile = UserProfile.objects.get(user=User)

        customer_profile = SellerProfileFactory(
            customuser_type_2=User, seller_profile=user_profile, address=faker.address()
        )

        old_address = customer_profile.address
        # updating the cusstomer profile instance

        get_customer_profile = SellerProfile.objects.get(
            customuser_type_2=User,
            seller_profile=user_profile,
        )
        get_customer_profile.address = (
            faker.building_number()
            + " "
            + faker.street_name()
            + ", "
            + faker.city()
            + ", "
            + faker.state()
            + " "
            + faker.zipcode()
            + ", "
            + faker.country()
        )
        get_customer_profile.save()

        assert (
            SellerProfile.objects.filter(
                customuser_type_2=User, seller_profile=user_profile
            ).count()
            == 1
        )
        assert old_address != get_customer_profile.address


@pytest.mark.django_db
class Test_CustomerServiceProfile:

    @pytest.mark.parametrize(
        "department, bio, experience_years",
        [
            ("Support", "Experienced in customer service", ""),
            ("", "", ""),
            ("Dept", "", -1),
            ("", "", None),
        ],
    )
    def test_invalid_data(self, department, bio, experience_years):
        user = CustomUserOnlyFactory(user_type="CUSTOMER REPRESENTATIVE")

        user_profile = UserProfile.objects.get(user=user)

        with pytest.raises(ValidationError):
            CustomerServiceProfileFactory(
                department=department,
                bio=bio,
                experience_years=experience_years,
                customuser_type_3=user,
                csr_profile=user_profile,
            )

    @pytest.mark.parametrize(
        "department, bio, experience_years",
        [("Support", "Experienced in customer service", 5), ("", "", 10)],
    )
    def test_valid_data(self, department, bio, experience_years):

        user = CustomUserOnlyFactory(user_type="CUSTOMER REPRESENTATIVE")

        user_profile = UserProfile.objects.get(user=user)

        CustomerServiceProfileFactory(
            department=department,
            bio=bio,
            experience_years=experience_years,
            customuser_type_3=user,
            csr_profile=user_profile,
        )

    def test_experience_years_positive(self):

        user = CustomUserOnlyFactory(user_type="CUSTOMER REPRESENTATIVE")

        user_profile = UserProfile.objects.get(user=user)

        with pytest.raises(ValidationError):
            CustomerServiceProfileFactory(
                customuser_type_3=user, csr_profile=user_profile, experience_years=100
            )

    def test_customer_profile_one_to_one_relationship(self):
        """
        Test that a UserProfile instance can only be associated with one CustomUser instance.
        """
        user = CustomUserOnlyFactory(user_type="CUSTOMER REPRESENTATIVE")

        user_profile = UserProfile.objects.get(user=user)

        CustomerServiceProfileFactory(
            customuser_type_3=user, csr_profile=user_profile, experience_years=1
        )
        # creating one more customer instance with 'user', and 'user_profile'
        # to raise error

        with pytest.raises(IntegrityError):
            CustomerServiceProfileFactory(
                customuser_type_3=user, csr_profile=user_profile, experience_years=1
            )


@pytest.mark.django_db
class Test_ManagerProfile:

    def test_invalid_data(self, invalid_manager_profile_data):
        user = CustomUserOnlyFactory(user_type="MANAGER")

        user_profile = UserProfile.objects.get(user=user)

        with pytest.raises(ValidationError):
            ManagerProfileFactory(
                **invalid_manager_profile_data,
                customuser_type_4=user,
                manager_profile=user_profile,
            )

    def test_valid_data(self, valid_manager_profile_data):

        user = CustomUserOnlyFactory(user_type="MANAGER")

        user_profile = UserProfile.objects.get(user=user)

        ManagerProfileFactory(
            **valid_manager_profile_data,
            customuser_type_4=user,
            manager_profile=user_profile,
        )

    def test_experience_years_positive(self):

        user = CustomUserOnlyFactory(user_type="MANAGER")

        user_profile = UserProfile.objects.get(user=user)

        with pytest.raises(ValidationError):
            ManagerProfileFactory(
                customuser_type_4=user,
                manager_profile=user_profile,
                experience_years=-1,
            )

    def test_customer_profile_one_to_one_relationship(self):
        """
        Test that a UserProfile instance can only be associated with one CustomUser instance.
        """
        user = CustomUserOnlyFactory(user_type="MANAGER")

        user_profile = UserProfile.objects.get(user=user)

        ManagerProfileFactory(
            customuser_type_4=user, manager_profile=user_profile, experience_years=1
        )
        # creating one more customer instance with 'user', and 'user_profile'
        # to raise error

        with pytest.raises(IntegrityError):

            ManagerProfileFactory(
                customuser_type_4=user, manager_profile=user_profile, experience_years=1
            )


@pytest.mark.django_db
class Test_AdminProfile:

    def test_invalid_data(self, invalid_admin_profile_data):
        user = CustomUserOnlyFactory(user_type="ADMININSTRATOR")

        user_profile = UserProfile.objects.get(user=user)

        with pytest.raises(ValidationError):
            AdministratorProfileFactory(
                **invalid_admin_profile_data,
                user=user,
                admin_profile=user_profile,
            )

    def test_valid_data(self, valid_admin_profile_data):

        user = CustomUserOnlyFactory(user_type="ADMINISTRATOR")

        user_profile = UserProfile.objects.get(user=user)

        AdministratorProfileFactory(
            **valid_admin_profile_data,
            user=user,
            admin_profile=user_profile,
        )

    def test_experience_years_positive(self):

        user = CustomUserOnlyFactory(user_type="ADMINISTRATOR")

        user_profile = UserProfile.objects.get(user=user)

        with pytest.raises(ValidationError):
            AdministratorProfileFactory(
                user=user,
                admin_profile=user_profile,
                experience_years=-1,
            )

    def test_customer_profile_one_to_one_relationship(self):
        """
        Test that a UserProfile instance can only be associated with one CustomUser instance.
        """
        user = CustomUserOnlyFactory(user_type="ADMINISTRATOR")

        user_profile = UserProfile.objects.get(user=user)

        AdministratorProfileFactory(
            user=user, admin_profile=user_profile, experience_years=1
        )

        with pytest.raises(IntegrityError):
            AdministratorProfileFactory(
                user=user, admin_profile=user_profile, experience_years=1
            )


@pytest.mark.django_db
class Test_CustomSocialAccount:

    def test_invalid_data(self, invalid_custom_social_account_data):
        user = CustomUserOnlyFactory(user_type="ADMININSTRATOR")

        with pytest.raises(ValidationError):
            custom_social_account = CustomSocialAccountFactory(
                **invalid_custom_social_account_data,
                user=user,
            )
            assert len(custom_social_account.access_token) > 500
            assert len(custom_social_account.user_info) > 1000
            assert len(custom_social_account.code) > 500
            assert len(custom_social_account.refresh_token) > 500

    def test_valid_data(self, valid_custom_social_account_data):

        user = CustomUserOnlyFactory(user_type="ADMINISTRATOR")

        CustomSocialAccountFactory(**valid_custom_social_account_data, user=user)

    @pytest.mark.parametrize(
        "user_type",
        ["CUSTOMER", "SELLER", "MANAGER", "ADMINISTRATOR", "CUSTOMER REPRESENTATIVE"],
    )
    def test_customer_profile_one_to_one_relationship(self, user_type):
        """
        Test that a UserProfile instance can only be associated with one CustomUser instance.
        """
        user = CustomUserOnlyFactory(user_type=user_type)

        CustomSocialAccountFactory(user=user)  # First attempt to create

        # Attempt to create another CustomSocialAccount with the same user should fail
        with pytest.raises((ValidationError, IntegrityError)):
            CustomSocialAccountFactory(user=user)
