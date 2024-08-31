import factory
from factory.django import DjangoModelFactory
import factory.faker
from faker import Faker
from Homepage.models import (
    CustomUser,
    UserProfile,
    CustomerProfile,
    SellerProfile,
    CustomerServiceProfile,
    ManagerProfile,
    AdministratorProfile,
    CustomSocialAccount,
)
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from tests.Homepage.Custom_Permissions import (
    CUSTOMER_CUSTOM_PERMISSIONS,
    CSR_CUSTOM_PERMISSIONS,
    ADMIN_CUSTOM_PERMISSIONS,
    SELLER_CUSTOM_PERMISSIONS,
    MANAGER_CUSTOM_PERMISSIONS,
)


fake = Faker()


class CustomUserOnlyFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker("user_name")
    email = factory.LazyAttribute(lambda _: Faker().unique.email())
    image = factory.Faker("image_url")
    user_google_id = None
    # password = factory.LazyAttribute(lambda x: fake.password())
    password = factory.PostGenerationMethodCall("set_password", "testpass123")

    @factory.lazy_attribute
    def user_type(self):
        return factory.Iterator([choice[0] for choice in CustomUser.USER_TYPE_CHOICES])

    @factory.lazy_attribute
    def is_staff(self):
        return self.user_type == "ADMINISTRATOR"

    @factory.lazy_attribute
    def is_superuser(self):
        return self.user_type == "ADMINISTRATOR"

    @factory.post_generation
    def assign_permissions(self, create, extracted, **kwargs):
        if not create:
            return

        custom_permissions = {}
        content_type = ContentType.objects.get_for_model(CustomUser)
        if self.user_type == "CUSTOMER":
            permissions = CUSTOMER_CUSTOM_PERMISSIONS
        elif self.user_type == "SELLER":
            permissions = SELLER_CUSTOM_PERMISSIONS
        elif self.user_type == "MANAGER":
            permissions = MANAGER_CUSTOM_PERMISSIONS
        elif self.user_type == "ADMINISTRATOR":
            permissions = ADMIN_CUSTOM_PERMISSIONS
        else:
            permissions = CSR_CUSTOM_PERMISSIONS

        for codename, description in permissions:
            user_permission = Permission.objects.get_or_create(
                codename=codename,
                name=description,
                content_type=content_type,
            )[0]

            custom_permissions[codename] = user_permission

        if self.user_type == "CUSTOMER":
            user_group, created = Group.objects.get_or_create(name="CUSTOMER")
        elif self.user_type == "SELLER":
            user_group, created = Group.objects.get_or_create(name="SELLER")
        elif self.user_type == "MANAGER":
            user_group, created = Group.objects.get_or_create(name="MANAGER")
        elif self.user_type == "ADMINISTRATOR":
            user_group, created = Group.objects.get_or_create(name="ADMINISTRATOR")
        else:
            user_group, created = Group.objects.get_or_create(
                name="CUSTOMER REPRESENTATIVE"
            )

        if created:
            for codename, permission in custom_permissions.items():
                try:
                    user_group.permissions.add(permission)
                except Permission.MultipleObjectsReturned:
                    print(f"Multiple objects returned for codename: {codename}")
            user_group.save()

    @factory.post_generation
    def create_user_profile(self, create, extracted, **kwargs):
        if not create:
            return

        UserProfile.objects.create(
            user=self,
            full_name="dummy_name",
            age=18,
            gender="Male",
            phone_number="+923074649892",
            city="dummy",
            country="NZ",
            postal_code="54400",
            shipping_address="default",
        )

    @classmethod
    def _create_user(cls, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

        email = cls.normalize_email(email)
        user = cls._meta.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=cls._meta.sqlalchemy_session)

        return user

    @classmethod
    def create_user(cls, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return cls._create_user(email, password, **extra_fields)

    @classmethod
    def create_superuser(cls, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return cls._create_user(email, password, **extra_fields)


class UserProfileOnlyFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(CustomUserOnlyFactory)
    full_name = factory.Faker("name")
    age = factory.Faker("random_int", min=18, max=90)
    gender = factory.Iterator(["Male", "Female", "Non-binary", "Other"])
    phone_number = factory.Iterator(
        ["+91 1234567890", "+917456987451", "+91-5689741236"]
    )
    city = factory.Faker("city")
    country = factory.Faker("country_code")
    postal_code = factory.Faker("postcode")
    shipping_address = factory.Faker("address")


class CustomUserFactory_Without_UserProfile_PostGeneration(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker("user_name")
    email = factory.LazyAttribute(lambda _: Faker().unique.email())
    image = factory.Faker("image_url")
    user_google_id = None
    password = factory.PostGenerationMethodCall("set_password", "testpass123")

    @factory.lazy_attribute
    def user_type(self):
        return factory.Iterator([choice[0] for choice in CustomUser.USER_TYPE_CHOICES])

    @factory.lazy_attribute
    def is_staff(self):
        return self.user_type == "ADMINISTRATOR"

    @factory.lazy_attribute
    def is_superuser(self):
        return self.user_type == "ADMINISTRATOR"

    @factory.post_generation
    def assign_permissions(self, create, extracted, **kwargs):
        if not create:
            return

        custom_permissions = {}
        content_type = ContentType.objects.get_for_model(CustomUser)
        if self.user_type == "CUSTOMER":
            permissions = CUSTOMER_CUSTOM_PERMISSIONS
        elif self.user_type == "SELLER":
            permissions = SELLER_CUSTOM_PERMISSIONS
        elif self.user_type == "MANAGER":
            permissions = MANAGER_CUSTOM_PERMISSIONS
        elif self.user_type == "ADMINISTRATOR":
            permissions = ADMIN_CUSTOM_PERMISSIONS
        else:
            permissions = CSR_CUSTOM_PERMISSIONS

        for codename, description in permissions:
            user_permission = Permission.objects.get_or_create(
                codename=codename,
                name=description,
                content_type=content_type,
            )[0]

            custom_permissions[codename] = user_permission

        if self.user_type == "CUSTOMER":
            user_group, created = Group.objects.get_or_create(name="CUSTOMER")
        elif self.user_type == "SELLER":
            user_group, created = Group.objects.get_or_create(name="SELLER")
        elif self.user_type == "MANAGER":
            user_group, created = Group.objects.get_or_create(name="MANAGER")
        elif self.user_type == "ADMINISTRATOR":
            user_group, created = Group.objects.get_or_create(name="ADMINISTRATOR")
        else:
            user_group, created = Group.objects.get_or_create(
                name="CUSTOMER REPRESENTATIVE"
            )

        if created:
            for codename, permission in custom_permissions.items():
                try:
                    user_group.permissions.add(permission)
                except Permission.MultipleObjectsReturned:
                    print(f"Multiple objects returned for codename: {codename}")
            user_group.save()

    @classmethod
    def _create_user(cls, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

        email = cls.normalize_email(email)
        user = cls._meta.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=cls._meta.sqlalchemy_session)

        return user

    @classmethod
    def create_user(cls, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return cls._create_user(email, password, **extra_fields)

    @classmethod
    def create_superuser(cls, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return cls._create_user(email, password, **extra_fields)


class UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration(
    DjangoModelFactory
):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(CustomUserFactory_Without_UserProfile_PostGeneration)
    full_name = factory.Faker("name")
    age = factory.Faker("random_int", min=18, max=130)
    gender = factory.Iterator(["Male", "Female", "Non-binary", "Other"])
    phone_number = factory.Iterator(
        ["+91 1234567890", "+917456987451", "+91-5689741236"]
    )
    city = factory.Faker("city")
    country = factory.Faker("country_code")
    postal_code = factory.Faker("postcode")
    shipping_address = factory.Faker("address")


class CustomerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomerProfile

    customer_profile = factory.SubFactory(
        UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration
    )
    customuser_type_1 = factory.SubFactory(
        CustomUserFactory_Without_UserProfile_PostGeneration
    )
    shipping_address = factory.LazyAttribute(lambda _: fake.address()[:255])
    wishlist = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=50))


class SellerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SellerProfile

    seller_profile = factory.SubFactory(UserProfileOnlyFactory)
    customuser_type_2 = factory.SubFactory(CustomUserOnlyFactory)
    address = factory.LazyAttribute(lambda _: fake.address())


class CustomerServiceProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomerServiceProfile

    csr_profile = factory.SubFactory(UserProfileOnlyFactory)
    customuser_type_3 = factory.SubFactory(CustomUserOnlyFactory)
    department = factory.LazyAttribute(lambda _: fake.sentence()[:50])
    bio = factory.LazyAttribute(lambda _: fake.text())
    experience_years = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=40))


class ManagerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ManagerProfile

    manager_profile = factory.SubFactory(UserProfileOnlyFactory)
    customuser_type_4 = factory.SubFactory(CustomUserOnlyFactory)
    team = factory.LazyAttribute(lambda _: fake.sentence()[:50])
    reports = factory.LazyAttribute(lambda _: fake.sentence()[:100])
    bio = factory.Faker("paragraph")
    experience_years = factory.Faker("random_int", min=1, max=40)


class AdministratorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AdministratorProfile

    admin_profile = factory.SubFactory(UserProfileOnlyFactory)
    user = factory.SubFactory(CustomUserOnlyFactory)
    bio = factory.LazyAttribute(lambda _: fake.sentence()[:250])
    experience_years = factory.Faker("random_int", min=1, max=40)


class CustomSocialAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomSocialAccount

    user = factory.SubFactory(CustomUserOnlyFactory)
    access_token = factory.LazyAttribute(
        lambda _: fake.sentence()
    )  # Exceeds 500 character limit
    user_info = factory.LazyAttribute(
        lambda _: fake.paragraph()
    )  # Exceeds 1000 character limit
    token_created_at = factory.Faker("date_time_this_year")
    code = factory.LazyAttribute(
        lambda _: fake.sentence()
    )  # Exceeds 500 character limit
    refresh_token = factory.LazyAttribute(
        lambda _: fake.sentence()
    )  # Exceeds 500 character limit


class LogInFormFactory(factory.Factory):
    class Meta:
        model = dict  # Since we are dealing with forms, we will generate dictionaries

    email = factory.LazyAttribute(lambda x: fake.email())
    password = factory.LazyAttribute(lambda x: fake.password())


class OTPFormFactory(factory.Factory):
    class Meta:
        model = dict

    otp = factory.LazyAttribute(lambda x: fake.random_int(min=100000, max=999999))


class E_MailForm_For_Password_ResetFactory(factory.Factory):
    class Meta:
        model = dict  # Using dict as the form takes a dictionary of data

    email = factory.LazyAttribute(lambda x: fake.email())


class CustomPasswordResetFormFactory(factory.Factory):
    class Meta:
        model = dict

    new_password1 = factory.LazyAttribute(lambda x: fake.password())
    new_password2 = factory.SelfAttribute("new_password1")
