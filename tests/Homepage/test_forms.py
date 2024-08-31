from django.forms.widgets import PasswordInput
from django.forms import (
    CharField,
    EmailField,
)
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
import pytest
import logging
from faker import Faker
from django.core.exceptions import ValidationError
from tests.Homepage.Homepage_factory import (
    UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration,
    LogInFormFactory,
    OTPFormFactory,
    E_MailForm_For_Password_ResetFactory,
    CustomPasswordResetFormFactory,
)
from Homepage.forms import (
    LogInForm,
    OTPForm,
    CustomUserImageForm,
    E_MailForm_For_Password_Reset,
    validate_password,
    CustomPasswordResetForm,
    UserProfileForm,
    CustomerProfileForm,
    SellerProfileForm,
    CustomerServiceProfileForm,
    ManagerProfileForm,
    AdministratorProfileForm,
)


fake = Faker()

# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)

from django.contrib.auth import get_user_model

CustomUser = get_user_model()


@pytest.fixture
def userprofile_form_data():
    def _userprofile_form_data(user_profile):
        # Test the form with valid data
        return {
            "full_name": user_profile.full_name,
            "age": user_profile.age,
            "gender": user_profile.gender,
            "phone_number": user_profile.phone_number,
            "city": user_profile.city,
            "country": "NZ",
            "postal_code": user_profile.postal_code,
            "shipping_address": user_profile.shipping_address,
        }

    return _userprofile_form_data


@pytest.fixture
def empty_userprofile_form():
    return {
        "full_name": "",
        "age": "",
        "gender": "",
        "phone_number": "",
        "city": "",
        "country": "",
        "postal_code": "",
        "shipping_address": "",
    }


def generate_paragraph(input):

    paragraph = fake.text(input)

    while len(paragraph) < input:
        paragraph += fake.sentence(1)[0] + " "

    return paragraph


@pytest.fixture(
    params=[
        {
            "team": generate_paragraph(10),
            "reports": generate_paragraph(100),
            "bio": "Experienced in customer service",
            "experience_years": 60,
        },
        {
            "team": generate_paragraph(10),
            "reports": generate_paragraph(10),
            "bio": "Experienced in customer service",
            "experience_years": 0,
        },
        {
            "team": "",
            "reports": "",
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
            "team": fake.sentence()[:10],  # Trim to maximum 100 characters
            "reports": fake.sentence()[:10],  # Trim to maximum 100 characters
            "bio": "Experienced in customer service",
            "experience_years": 40,
        },
        {
            "team": fake.sentence()[:10],  # Trim to maximum 100 characters
            "reports": fake.sentence()[:10],  # Trim to maximum 100 characters
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
            "bio": fake.sentence()[:10],
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
            "bio": fake.sentence()[:10],
            "experience_years": 40,
        },
        {
            "bio": fake.sentence()[:250],
            "experience_years": 1,
        },
    ]
)
def valid_admin_profile_data(request):
    return request.param


@pytest.mark.django_db
class Test_LoginForm:
    def test_login_form_valid_data(self):
        form_data = LogInFormFactory()
        form = LogInForm(data=form_data)

        assert form.is_valid()

        assert isinstance(form.fields["email"], EmailField)
        assert isinstance(form.fields["password"], CharField)
        assert isinstance(form.fields["password"].widget, PasswordInput)

    def test_login_form_invalid_email(self):
        form_data = LogInFormFactory(email="invalid-email")
        form = LogInForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_login_form_empty_password(self):
        form_data = LogInFormFactory(password="")
        form = LogInForm(data=form_data)
        assert not form.is_valid()
        assert "password" in form.errors


@pytest.mark.django_db
class Test_OTPForm:
    def test_otp_form_invalid_otp(self):
        form_data = OTPFormFactory(otp=99999)  # Less than 6 digits
        form = OTPForm(data=form_data)
        assert not form.is_valid()
        assert "otp" in form.errors

    def test_otp_form_empty_otp(self):
        form_data = OTPFormFactory(otp=None)
        form = OTPForm(data=form_data)
        assert not form.is_valid()
        assert "otp" in form.errors


@pytest.mark.django_db
class Test_EmailFormForPasswordReset:
    def test_email_form_valid_data(self):
        form_data = E_MailForm_For_Password_ResetFactory()
        form = E_MailForm_For_Password_Reset(data=form_data)
        assert form.is_valid()

    def test_email_form_invalid_email(self):
        form_data = E_MailForm_For_Password_ResetFactory(email="invalid-email")
        form = E_MailForm_For_Password_Reset(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_email_form_empty_email(self):
        form_data = E_MailForm_For_Password_ResetFactory(email="")
        form = E_MailForm_For_Password_Reset(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors


@pytest.mark.parametrize(
    "password, is_valid",
    [
        ("Password1!", True),
        ("password", False),
        ("12345678", False),
        ("Password", False),
        ("Password!", False),
        ("Password1", False),
    ],
)
def test_validate_password(password, is_valid):
    if is_valid:
        validate_password(password)  # Should not raise ValidationError
    else:
        with pytest.raises(ValidationError):
            validate_password(password)


@pytest.mark.django_db
class Test_CustomPasswordResetForm:
    def test_custom_password_reset_form_valid_data(self):
        form_data = CustomPasswordResetFormFactory()
        form = CustomPasswordResetForm(data=form_data)
        assert form.is_valid()

    def test_custom_password_reset_form_password_mismatch(self):
        form_data = CustomPasswordResetFormFactory(new_password2="differentPassword")
        form = CustomPasswordResetForm(data=form_data)
        assert form.is_valid()
        assert not "new_password2" in form.errors

    def test_custom_password_reset_form_invalid_password(self):
        form_data = CustomPasswordResetFormFactory(new_password1="password")
        form = CustomPasswordResetForm(data=form_data)
        assert not form.is_valid()
        assert "new_password1" in form.errors

    def test_custom_password_reset_form_empty_password(self):
        form_data = CustomPasswordResetFormFactory(new_password1="", new_password2="")
        form = CustomPasswordResetForm(data=form_data)
        assert not form.is_valid()
        assert "new_password1" in form.errors
        assert "new_password2" in form.errors


@pytest.mark.django_db
class Test_CustomImageForm:
    def test_successfull_image_upload(self):

        # Create an image file using Pillow
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # Create a SimpleUploadedFile from the image bytes
        uploaded_file = SimpleUploadedFile(
            "test_image.jpg", image_bytes.read(), content_type="image/jpeg"
        )

        # Create the form data
        data = {}
        file_dict = {"image": uploaded_file}
        form = CustomUserImageForm(data, file_dict)

        # Print the form errors for debugging
        print(f"Form errors: {form.errors}")

        # Assert that the form is valid
        assert form.is_valid()

    def test_custom_user_image_form_no_image(self):
        form_data = {"image": None}
        form = CustomUserImageForm(data=form_data)
        assert form.is_valid()
        assert (
            form.cleaned_data["image"]
            == CustomUser._meta.get_field("image").get_default()
        )


@pytest.mark.django_db
class Test_UserProfileForm:
    def test_user_profile_form(self, userprofile_form_data):
        # Create a user profile using the factory
        user_profile = (
            UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration()
        )

        # Get the data from fixture
        form_data = userprofile_form_data(user_profile)

        form = UserProfileForm(data=form_data)
        assert not form.is_valid()
        assert "phone_number" in form.errors

    def test_user_profile_form_invalid_age(self, userprofile_form_data):
        profile = (
            UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration(
                age=17
            )
        )  # Invalid age, less than 18
        # Get the data from fixture
        form_data = userprofile_form_data(profile)

        form = UserProfileForm(data=form_data)
        assert not form.is_valid()
        assert "age" in form.errors

    def test_user_profile_form_empty_fields(self, empty_userprofile_form):
        # create an empty form with all fields empty ""
        form_data = empty_userprofile_form

        form = UserProfileForm(data=form_data)
        assert not form.is_valid()
        assert "full_name" in form.errors
        assert "age" in form.errors
        assert "gender" in form.errors
        assert "phone_number" in form.errors
        assert "city" in form.errors
        assert "country" in form.errors
        assert "postal_code" in form.errors
        assert "shipping_address" in form.errors

    def test_user_profile_form_invalid_gender(self, userprofile_form_data):
        profile = (
            UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration(
                gender="InvalidGender"
            )
        )  # Invalid gender

        # make a dictionary for form
        form_data = userprofile_form_data(profile)

        form = UserProfileForm(data=form_data)
        assert not form.is_valid()
        assert "gender" in form.errors

    def test_user_profile_form_invalid_phone_number(self, userprofile_form_data):
        profile = (
            UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration(
                phone_number="InvalidPhoneNumber"
            )
        )  # Invalid phone number

        # make a dictionary for the form
        form_data = userprofile_form_data(profile)

        form = UserProfileForm(data=form_data)
        assert not form.is_valid()
        assert "phone_number" in form.errors


@pytest.mark.django_db
class Test_CustomerProfileForm:

    @pytest.mark.parametrize(
        "shipping_address, wishlist",
        [(fake.address(), fake.random_int(min=1, max=50))],
    )
    def test_customer_profile_form(self, shipping_address, wishlist):

        form_data = {"shipping_address": shipping_address, "wishlist": wishlist}

        form = CustomerProfileForm(form_data)
        assert form.is_valid()

    def test_customer_profile_form_empty_fields(self):
        form_data = {"shipping_address": "", "wishlist": ""}

        form = CustomerProfileForm(form_data)
        assert not form.is_valid()
        assert "wishlist" in form.errors
        assert "Valid Whislist is required" in str(form.errors["wishlist"])

    @pytest.mark.django_db
    def test_clean_wishlist_valid(self):
        form_data = {
            "shipping_address": "House No. 111, Block A-4, Johar Town.",
            "wishlist": 25,
        }
        form = CustomerProfileForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data["wishlist"] == 25


@pytest.mark.django_db
class Test_SellerProfileForm:

    @pytest.mark.parametrize(
        "address, valid",
        [(fake.address(), True), (fake.address()[:9], False), ("", False)],
    )
    def test_seller_profile_form(self, address, valid):

        form_data = {"address": address}

        form = SellerProfileForm(form_data)
        assert form.is_valid() == valid

    @pytest.mark.django_db
    def test_clean_address_valid(self):

        form_data = {"address": "House No. 111, Block A-4, Johar Town."}
        form = SellerProfileForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data["address"] == form_data["address"]


@pytest.mark.django_db
class Test_CSR_ProfileForm:

    @pytest.mark.parametrize(
        "department, bio, experience_years, valid",
        [
            ("Support", "Experienced in customer service", "", False),
            ("", "", "", False),
            ("Dept", "", -1, False),
            ("", "", 40, True),
            ("", "", 41, False),
        ],
    )
    def test_csr_profile_form(self, department, bio, experience_years, valid):

        form_data = {
            "department": department,
            "bio": bio,
            "experience_years": experience_years,
        }

        form = CustomerServiceProfileForm(form_data)
        assert form.is_valid() == valid

    @pytest.mark.django_db
    def test_clean_experience_years(self):

        form_data = {
            "department": fake.text()[:50],
            "bio": fake.sentence()[:500],
            "experience_years": fake.random_int(min=1, max=40),
        }
        form = CustomerServiceProfileForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data["experience_years"] == form_data["experience_years"]


@pytest.mark.django_db
class Test_ManagerProfileForm:

    def test_manager_profile_form_with_invalid_data(self, invalid_manager_profile_data):

        form = ManagerProfileForm(data=invalid_manager_profile_data)
        assert not form.is_valid()

    def test_manager_profile_form_with_valid_data(self, valid_manager_profile_data):

        form = ManagerProfileForm(data=valid_manager_profile_data)
        assert form.is_valid()

    @pytest.mark.django_db
    def test_clean_experience_years(self, valid_manager_profile_data):

        form_data = valid_manager_profile_data

        form = ManagerProfileForm(data=valid_manager_profile_data)
        assert form.is_valid()
        assert form.cleaned_data["experience_years"] == form_data["experience_years"]


@pytest.mark.django_db
class Test_AdminProfileForm:

    def test_manager_profile_form_with_invalid_data(self, invalid_admin_profile_data):

        form = AdministratorProfileForm(data=invalid_admin_profile_data)
        assert not form.is_valid()

    def test_manager_profile_form_with_valid_data(self, valid_admin_profile_data):

        form = AdministratorProfileForm(data=valid_admin_profile_data)
        assert form.is_valid()

    @pytest.mark.django_db
    def test_clean_experience_years(self, valid_admin_profile_data):

        form_data = valid_admin_profile_data

        form = AdministratorProfileForm(data=valid_admin_profile_data)
        assert form.is_valid()
        assert form.cleaned_data["experience_years"] == form_data["experience_years"]
