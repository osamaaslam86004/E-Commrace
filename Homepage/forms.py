from Homepage.models import (
    CustomUser,
    UserProfile,
    CustomerProfile,
    SellerProfile,
    CustomerServiceProfile,
    ManagerProfile,
    AdministratorProfile,
)
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re
from django_countries.widgets import CountrySelectWidget


class SignUpForm(UserCreationForm):
    USER_TYPE_CHOICES = CustomUser.USER_TYPE_CHOICES
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        label="User Type",
        widget=forms.Select(attrs={"placeholder": "Select User Type"}),
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "user_type",
            "password1",
            "password2",
        ]
        exclude = ["user_google_id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={"placeholder": "Password"}
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={"placeholder": "Confirm Password"}
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data["user_type"]
        if commit:
            user.save()
            # Create UserProfile for the user
            UserProfile.objects.create(
                user=user,
                full_name="",
                age=18,
                gender="",
                phone_number="",
                city="",
                country="",
                postal_code="",
            )

            return user


class CustomUserImageForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ["image"]

    def clean_image(self):
        if self.cleaned_data["image"] is None:
            return CustomUser._meta.get_field("image").get_default()
        return self.cleaned_data["image"]


class LogInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class OTPForm(forms.Form):
    otp = forms.IntegerField(
        min_value=100000,
        max_value=999999,
        widget=forms.NumberInput(attrs={"maxlength": "6"}),
        label="OTP",
        help_text="Enter a 6-digit OTP",
    )


def validate_password(value):
    if (
        not re.search(r"[A-Za-z]", value)
        or not re.search(r"[0-9]", value)
        or not re.search(r'[!@#$%^&*(),.?":{}|<>]', value)
    ):
        raise ValidationError(
            "Password must contain at least one alphabet, one numeric value, and one special character (!, @, #, $, etc.)."
        )


class E_MailForm_For_Password_Reset(forms.Form):
    email = forms.EmailField(label="E-mail", help_text="Enter a E-Mail")


class CustomPasswordResetForm(forms.Form):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
                "placeholder": "Enter password",
            }
        ),
        validators=[validate_password],
        help_text="Password must contain at least one alphabet, one numeric value, and one special character (!, @, #, $, etc.).",
    )
    new_password2 = forms.CharField(
        label="New Password Confirmation",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
                "placeholder": "Confirm password",
            }
        ),
    )

    # def clean(self):
    #     cleaned_data = super().clean()
    #     new_password1 = cleaned_data.get("new_password1")
    #     new_password2 = cleaned_data.get("new_password2")

    #     if new_password1 and new_password2 and new_password1 != new_password2:
    #         raise ValidationError({
    #             "new_password2": "The two password fields must match.",
    #         })


class UserProfileForm(forms.ModelForm):  # no need to validate max_length
    #  this model field will allow only max_character in the form
    # if user try, then django form rendering will prevent this
    GENDER_CHOICES = UserProfile.GENDER_CHOICES
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label="Gender Type",
        widget=forms.Select(attrs={"placeholder": "Select Gender Type"}),
    )

    def clean_age(self):
        if self.cleaned_data["age"] is None:
            raise ValidationError("Valid age is required,")
        if self.cleaned_data["age"] < 18 or self.cleaned_data["age"] > 130:
            raise ValidationError("Valid age is required, Hint: 0 to 130")
        return self.cleaned_data["age"]

    class Meta:
        model = UserProfile
        fields = [
            "full_name",
            "age",
            "gender",
            "phone_number",
            "city",
            "country",
            "postal_code",
            "shipping_address",
        ]
        exclude = ["user"]
        labels = {
            "full_name": "Full Name",
            "age": "Age",
            "gender": "Gender",
            "phone_number": "Phone Number",
            "city": "City",
            "country": "Country",
            "postal_code": "Postal Code",
            "shipping_address": "Shipping Address",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Enter your full name"}),
            "age": forms.NumberInput(attrs={"placeholder": "Enter your age"}),
            "city": forms.TextInput(attrs={"placeholder": "Enter your city name"}),
            "country": CountrySelectWidget(
                attrs={"class": "selectpicker", "data-live-search": "true"}
            ),
            "postal_code": forms.TextInput(
                attrs={"placeholder": "Enter your postal code"}
            ),
            "shipping_address": forms.TextInput(
                attrs={"placeholder": "Enter shipping address"}
            ),
            "phone_number": PhoneNumberPrefixWidget(),
        }
        help_texts = {
            "full_name": "Enter your full name as it appears on official documents.",
            "age": "Enter your age in years (1-130).",
            "gender": "Specify your gender (e.g., Male, Female, Other).",
            "phone_number": "Provide a valid phone number for contact.",
            "city": "Enter the name of your city of residence.",
            "country": "Enter the name of your country of residence.",
            "postal_code": "54440.",
            "shipping_address": "House No/Apartment,  Block, Town",
        }


class CustomerProfileForm(forms.ModelForm):

    def clean_wishlist(self):
        wishlist = self.cleaned_data["wishlist"]

        if not wishlist:
            raise ValidationError("Valid Whislist is required,")
        if wishlist <= 0 or wishlist >= 50:
            raise ValueError("Valid whishlist is required, Hint: 0 to 50")
        return wishlist

    class Meta:
        model = CustomerProfile
        fields = ["shipping_address", "wishlist"]
        labels = {
            "shipping_address": "Shipping Address",
            "wishlist": "Wishlist",
        }
        widgets = {
            "shipping_address": forms.TextInput(
                attrs={
                    "placeholder": "Enter your shipping address as it appears on official documents"
                }
            ),
            "wishlist": forms.NumberInput(
                attrs={"placeholder": "Enter number of items"}
            ),
        }
        help_texts = {
            "shipping_address": "House No. 111, Block A-4, Johar Town.",
            "wishlist": "Enter amount 1-100.",
        }


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ["address"]
        labels = {
            "address": "Address",
        }
        widgets = {
            "address": forms.TextInput(
                attrs={
                    "placeholder": "Enter your warehouse address as it appears on official documents"
                }
            ),
        }
        help_texts = {
            "address": "Plaza No. 111, Ground Floor, Block B-4, Iqbal Town.",
        }

    def clean_address(self):
        address = self.cleaned_data["address"]
        if len(address) < 10:
            raise ValidationError(
                "Shipping address must be at least 10 characters long."
            )
        return address


class CustomerServiceProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerServiceProfile
        fields = ["department", "bio", "experience_years"]
        labels = {
            "department": "Department",
            "bio": "Bio",
            "experience_years": "Experience",
        }
        widgets = {
            "department": forms.TextInput(
                attrs={"placeholder": "Enter your department name"}
            ),
            "bio": forms.TextInput(attrs={"placeholder": "Name, Place, etc."}),
            "experience_years": forms.NumberInput(
                attrs={"placeholder": "Enter your experience"}
            ),
        }
        help_texts = {
            "department": "",
            "bio": "Your Bio in 500 characters.",
            "experience_years": "Your experience in years",
        }

    def clean_experience_years(self):
        experience_years = self.cleaned_data["experience_years"]

        if not experience_years:
            raise ValidationError("Experience years is required.")
        if experience_years < 1 or experience_years > 40:
            raise ValidationError("Experience must be 1 to 40 years.")
        return experience_years


class ManagerProfileForm(forms.ModelForm):
    class Meta:
        model = ManagerProfile
        fields = ["team", "reports", "bio", "experience_years"]
        labels = {
            "team": "Team",
            "reports": "Reports",
            "bio": "Bio",
            "experience_years": "Experience Years",
        }
        widgets = {
            "team": forms.TextInput(attrs={"placeholder": "Enter your team name"}),
            "reports": forms.TextInput(attrs={"placeholder": "Enter your report"}),
            "bio": forms.TextInput(attrs={"placeholder": "Enter your bio"}),
            "experience_years": forms.NumberInput(
                attrs={"placeholder": "Enter your experience"}
            ),
        }
        help_texts = {
            "team": "Product Listing, Accounts, etc",
            "reports": "Enter your report in words (1-100).",
            "bio": "Specify your bio (e.g., Name, Place, Other) Hint: [1 to 500 characters].",
            "experience_years": "(1 - 40)",
        }

    def clean_experience_years(self):
        experience_years = self.cleaned_data["experience_years"]

        if not experience_years:
            raise ValidationError("Experience years is required.")
        if experience_years < 1 or experience_years > 40:
            raise ValidationError("Experience must be 1 to 40 years.")
        return experience_years


class AdministratorProfileForm(forms.ModelForm):
    class Meta:
        model = AdministratorProfile
        fields = ["bio", "experience_years"]
        labels = {
            "bio": "Bio",
            "experience_years": "Experience Years",
        }
        widgets = {
            "bio": forms.TextInput(attrs={"placeholder": "Enter your bio"}),
            "experience_years": forms.NumberInput(
                attrs={"placeholder": "Enter experience in years"}
            ),
        }
        help_texts = {
            "bio": "Specify your bio (e.g., Name, Place, Other) [1-500 characyers].",
            "experience_years": "(1 - 40)",
        }

    def clean_experience_years(self):
        experience_years = self.cleaned_data["experience_years"]

        if not experience_years:
            raise ValidationError("Experience years is required.")
        if experience_years < 1 or experience_years > 40:
            raise ValidationError("Experience must be 1 to 40 years.")
        return experience_years
