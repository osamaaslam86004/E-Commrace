from random import randint

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import carrier, parse, region_code_for_number, timezone
from phonenumbers.geocoder import description_for_number


class CustomUserManager(BaseUserManager):
    def generate_unique_phone_number():
        while True:
            random_number = f"+92307{randint(1000000, 9999999)}"
            if not UserProfile.objects.filter(phone_number=random_number).exists():
                return random_number

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        # Set is_staff based on user_type
        if extra_fields.get("user_type") != "CUSTOMER" and user.is_staff != True:
            user.is_staff = True

        user.save(using=self._db)

        # Create a UserProfile for the user
        try:
            phone_number = self.generate_unique_phone_number()

            UserProfile.objects.create(
                user=user,
                full_name="dummy_name",
                age=18,
                gender="Male",
                phone_number=phone_number,
                city="dummy",
                country="PK",
                postal_code="54400",
                shipping_address="default",
            )
        except Exception as e:
            print(f"Error creating UserProfile for {user.email}: {e}")

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("CUSTOMER", "Customer"),
        ("SELLER", "Seller"),
        ("CUSTOMER REPRESENTATIVE", "Customer Service Representative"),
        ("MANAGER", "Manager"),
        ("ADMINISTRATOR", "Administrator"),
    )

    email = models.EmailField(
        verbose_name="email address", max_length=255, unique=True, blank=False
    )
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES)
    image = models.ImageField(
        upload_to="images/",
        blank=True,
        default="https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico",
    )
    user_google_id = models.IntegerField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Non-binary", "Non-binary"),
        ("Other", "Other"),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, name="user")
    full_name = models.CharField(max_length=50, blank=False)
    age = models.IntegerField(blank=False, default=18)
    gender = models.CharField(max_length=15, blank=False, choices=GENDER_CHOICES)
    phone_number = PhoneNumberField(blank=False, unique=True, null=False)
    city = models.CharField(max_length=100, blank=False)
    country = CountryField(
        multiple=False,
        blank_label="(select country)",
        blank=False,
        null=False,
        default="PK",
    )
    postal_code = models.CharField(max_length=20, blank=False)
    shipping_address = models.CharField(max_length=1000, blank=False)

    @staticmethod
    def generate_unique_phone_number(user_id):
        """
        Generate a unique phone number with the randomint as the last digits.
        If the number is already taken, retry with different variations.
        """
        base_number = "+92307"
        attempts = 0
        max_attempts = 10  # Avoid infinite loops

        while attempts < max_attempts:
            random_number = f"+92307{randint(1000000, 9999999)}"
            if not UserProfile.objects.filter(phone_number=random_number).exists():
                return random_number

            attempts += 1

        raise ValueError(
            "Could not generate a unique phone number after multiple attempts."
        )

    if settings.DEBUG == False:

        def clean(self):
            super().clean()
            if not self.age:
                raise ValidationError("Valid age is required,")
            if self.age < 18 or self.age > 130:
                raise ValidationError("Valid age is required, Hint: 0 to 130")

            # Parse the phone number
            parsed_number = parse(str(self.phone_number), None)
            print(parsed_number)

            # Validate phone number and check country match
            # if not is_valid_number(parsed_number):
            #     raise ValidationError("Parsing Error: Invalid phone number format.")

            """country code PK for Pakistan from phonenumber field is matched
            with country.code == PK from django_countries"""

            phone_country = region_code_for_number(parsed_number)
            print(f" phone Number field country: {phone_country}")
            print(f" country field country: {self.country.code}")

            if phone_country != self.country.code:
                raise ValidationError(
                    f"The phone number does not belong to the country {self.country.name}."
                )

            # Get region (state or province)
            self.region = description_for_number(parsed_number, "en")
            print(f"Region: {self.region}")

            # Get time zones)
            time_zones = timezone.time_zones_for_number(parsed_number)
            print(time_zones)  # Example: ('America/Los_Angeles',)

            carrier_name = carrier.name_for_number(parsed_number, "en")
            print(carrier_name)  # Example: "AT&T" or "Verizon"

    def save(self, *args, **kwargs):
        if settings.DEBUG == False:
            self.clean()

        """Assign a unique phone number if not provided."""
        if not self.phone_number:
            self.phone_number = UserProfile.generate_unique_phone_number()

        super().save(*args, **kwargs)


class CustomerProfile(models.Model):
    customer_profile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, name="customer_profile", default=None
    )
    customuser_type_1 = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, name="customuser_type_1", default=None
    )
    shipping_address = models.CharField(max_length=255, blank=True)
    wishlist = models.IntegerField(blank=True)

    def clean(self):
        super().clean()
        if not self.wishlist:
            raise ValidationError("Valid Whislist is required,")
        if self.wishlist <= 0 or self.wishlist >= 50:
            raise ValidationError("Valid whishlist is required, Hint: 0 to 50")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class SellerProfile(models.Model):
    class Meta:
        permissions = [
            ("seller_publish_post", "Can publish post"),
            ("seller_feature_post", "Can feature post"),
        ]

    seller_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        name="seller_profile",
    )
    customuser_type_2 = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        name="customuser_type_2",
    )
    address = models.CharField(max_length=100, blank=False, default="Dummy Addess")

    def clean(self):
        super().clean()
        if not self.address:
            raise ValueError("Shipping address is required.")
        if len(self.address) < 10:
            raise ValidationError(
                "Shipping address must be at least 10 characters long."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class CustomerServiceProfile(models.Model):
    csr_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        name="csr_profile",
    )
    customuser_type_3 = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        name="customuser_type_3",
    )
    department = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    experience_years = models.PositiveIntegerField(blank=False)

    def clean(self):
        super().clean()
        if not self.experience_years or self.experience_years < 1:
            raise ValidationError("Experience years is required.")
        if self.experience_years > 40:
            raise ValidationError("Experience must be 1 to 40 years.")
        if len(self.department) > 50:
            raise ValidationError("Department must be 0 to 50 years.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ManagerProfile(models.Model):
    manager_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        name="manager_profile",
    )
    customuser_type_4 = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        name="customuser_type_4",
    )
    team = models.CharField(max_length=50, blank=True)
    reports = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    experience_years = models.PositiveIntegerField(blank=False)

    def clean(self):
        super().clean()
        if not self.experience_years or self.experience_years < 1:
            raise ValidationError("Experience years is required.")
        if self.experience_years > 40:
            raise ValidationError("Experience must be 1 to 40 years.")
        if len(self.team) < 0 or len(self.team) > 50:
            raise ValueError("Department must be 0 to 50 years.")
        if len(self.reports) < 0 or len(self.reports) > 100:
            raise ValidationError("Department must be 0 to 50 years.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class AdministratorProfile(models.Model):
    class Meta:
        permissions = [
            ("admin_publish_post", "Can publish post"),
            ("admin_feature_post", "Can feature post"),
        ]

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="customuser_type_5",
        null=True,
    )
    admin_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        name="admin_profile",
    )
    bio = models.TextField(blank=True, max_length=500)
    experience_years = models.PositiveIntegerField(blank=False, default=1)

    def clean(self):
        super().clean()
        if not self.experience_years or self.experience_years < 1:
            raise ValidationError("Experience years is required.")
        if self.experience_years > 40:
            raise ValidationError("Experience must be 1 to 40 years.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class CustomSocialAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    """
        # access token Expirey 1 hour set by Google
    """
    access_token = models.TextField(max_length=500, blank=True)
    user_info = models.TextField(max_length=1000)
    token_created_at = models.DateTimeField(auto_now_add=True)
    code = models.TextField(max_length=500)
    refresh_token = models.TextField(max_length=500, blank=True, null=True)

    # def clean(self):
    #     super().clean()
    #     if len(self.code) > 500:
    #         raise ValidationError("code must be 0 to 500 characters.")
    #     if len(self.refresh_token) > 500:
    #         raise ValidationError("refresh token must be 0 to 500 characters.")
    #     if len(self.access_token) > 500:
    #         raise ValidationError("access token must be 0 to 500 characters.")
    #     if len(self.user_info) > 1000:
    #         raise ValidationError("user_info must be 0 to 1000 characters.")

    # def save(self, *args, **kwargs):
    #     self.clean()
    #     super().save(*args, **kwargs)
