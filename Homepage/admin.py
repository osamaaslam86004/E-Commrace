import logging
from re import T

# Get the logger defined in settings.py
logger = logging.getLogger("admin")
from django.core.exceptions import ValidationError
from django.contrib import admin, messages
from django.utils.html import format_html
from django import forms
from Homepage.forms import (
    CustomUserAdminForm,
    UserProfileForm,
    UserProfileFormAdmin,
    CustomerProfileAdminForm,
    SellerProfileAdminForm,
    CustomerServiceProfileAdminForm,
)
from django.contrib import admin

from Homepage.models import (
    AdministratorProfile,
    CustomerProfile,
    CustomerServiceProfile,
    CustomUser,
    ManagerProfile,
    SellerProfile,
    UserProfile,
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserAdminForm
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES)
    model = CustomUser
    list_display = [
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "user_type",
        "date_joined",
        "last_login",
    ]
    list_filter = ["user_type"]
    ordering = ["username"]
    fieldsets = (
        ("OAuth", {"fields": ("email", "username", "password")}),
        (
            "Additional Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "is_staff",
                    "is_superuser",
                    "user_type",
                    "date_joined",
                    "last_login",
                ),
            },
        ),
    )
    search_fields = ["email", "username", "first_name", "last_name"]
    filter_horizontal = ()

    # Customize the add view
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_staff",
                    "user_type",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        # Set the user's type based on the field in the form (e.g., user_type)
        obj.user_type = form.cleaned_data.get("user_type", "customer")

        is_new_user = not change  # Check if this is a new user
        super().save_model(request, obj, form, change)

        if is_new_user:  # Create a UserProfile for the new user
            UserProfile.objects.get_or_create(
                user=obj,
                defaults={
                    "full_name": "dummy_name",
                    "age": 18,
                    "gender": "Male",
                    "phone_number": "+923074649892",
                    "city": "dummy",
                    "country": "PK",
                    "postal_code": "54400",
                    "shipping_address": "default",
                },
            )
            messages.success(
                request,
                format_html(
                    'The User Profile <span style="color: blue;">{}</span> has been created successfully.',
                    obj,
                ),
            )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileFormAdmin
    list_display = [
        "full_name",
        "age",
        "gender",
        "phone_number",
        "city",
        "country",
        "postal_code",
        "user",
    ]
    list_filter = ["gender", "city", "country"]
    search_fields = ["user__username", "user__email", "full_name", "phone_number"]
    list_per_page = 20

    fieldsets = (
        ("User", {"fields": ("user",)}),
        (
            "Personal Information",
            {"fields": ("full_name", "age", "gender", "phone_number")},
        ),
        (
            "Location",
            {"fields": ("city", "country", "postal_code")},
        ),
        ("Shipping Address", {"fields": ("shipping_address",)}),
    )

    readonly_fields = ("user",)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + (
                "phone_number",
                "country",
            )  # Make 'phone_number' read-only
        return self.readonly_fields

    def has_add_permission(self, request):
        # Disabling the "Add" button for UserProfile
        return False

    # def get_exclude(self, request, obj=None):
    #     if obj:  # Editing an existing object
    #         return ("user",)  # Hide 'user' field
    #     return ()


@admin.register(CustomerProfile)
class CustomerAdmin(admin.ModelAdmin):
    form = CustomerProfileAdminForm
    list_display = [
        "shipping_address",
        "wishlist",
        "customuser_type_1",
        "get_customer_profile",
    ]
    list_filter = ["shipping_address", "customuser_type_1"]
    ordering = [
        "wishlist",
    ]
    row_id_fields = ("customuser_type_1",)
    fieldsets = (
        ("User Data", {"fields": ("customuser_type_1",)}),
        ("Shipping Address & Wishlist", {"fields": ("shipping_address", "wishlist")}),
    )
    search_fields = [
        "shipping_address",
        "customer_profile__full_name",
        "customuser_type_1__email",
    ]
    autocomplete_fields = ["customuser_type_1"]

    def get_customer_profile(self, obj):
        return str(obj.customer_profile.full_name) if obj else None

    get_customer_profile.short_description = "UserProfile Full-Name"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(
            request, obj
        )  # Get existing readonly fields
        if obj:
            readonly_fields += (
                "customuser_type_1",
            )  # Add customer_profile if obj exists
        return readonly_fields

    def save_model(self, request, obj, form, change):
        # If this is a new object (not being changed), we need to handle it differently
        if not change:
            user = form.cleaned_data.get("customuser_type_1")
            shipping_address = form.cleaned_data.get("shipping_address")
            wishlist = form.cleaned_data.get("wishlist")

            # Ensure that the UserProfile exists for the selected CustomUser
            user_profile = (
                UserProfile.objects.filter(user__id=user.id).defer("user").first()
            )

            if not user_profile:
                raise ValidationError(
                    "The selected CustomUser does not have an associated UserProfile."
                )
            try:
                # Assign values to the CustomerProfile instance
                obj.customuser_type_1 = user
                obj.customer_profile = user_profile  # Assign existing UserProfile
                obj.shipping_address = shipping_address
                obj.wishlist = wishlist
            except:
                logger.debug(f"Saving CustomerProfile with: {obj.__dict__}")

        # Call the superclass method to save
        super().save_model(request, obj, form, change)


@admin.register(SellerProfile)
class SellerAdmin(admin.ModelAdmin):
    form = SellerProfileAdminForm
    list_display = ["address", "customuser_type_2", "get_seller_profile"]
    list_filter = ["address", "customuser_type_2__email", "seller_profile__full_name"]
    ordering = ["address"]
    fieldsets = (
        ("User Data", {"fields": ("customuser_type_2",)}),
        ("Shiping Address", {"fields": ("address",)}),
    )
    search_fields = [
        "address",
        "seller_profile__full_name",
        "customuser_type_2__email",
    ]
    # Add descriptive text for the search box
    search_help_text = "Search by address, full name, email."
    row_id_fields = ("customuser_type_2",)
    autocomplete_fields = ["customuser_type_2"]
    filter_horizontal = ()

    def get_seller_profile(self, obj):
        return str(obj.seller_profile.full_name) if obj else None

    get_seller_profile.short_description = "UserProfile Full-Name"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(
            request, obj
        )  # Get existing readonly fields
        if obj:
            readonly_fields += (
                "customuser_type_2",
            )  # Add customer_profile if obj exists
        return readonly_fields

    def save_model(self, request, obj, form, change):

        user = form.cleaned_data.get("customuser_type_2")
        shipping_address = form.cleaned_data.get("address")

        # If this is a new object (not being changed), we need to handle it differently
        if not change:
            # Ensure that the UserProfile exists for the selected CustomUser
            user_profile = (
                UserProfile.objects.filter(user__id=user.id).defer("user").first()
            )

            if not user_profile:
                form.add_error(
                    "customuser_type_2",
                    "The selected CustomUser does not have an associated UserProfile",
                )
                return
            try:
                # Assign values to the CustomerProfile instance
                obj.customuser_type_2 = user
                obj.seller_profile = user_profile  # Assign existing UserProfile
                obj.address = shipping_address
            except:
                logger.debug(f"Saving CustomerProfile with: {obj.__dict__}")

        # Call the superclass method to save
        super().save_model(request, obj, form, change)


@admin.register(CustomerServiceProfile)
class CustomerServiceProfileAdmin(admin.ModelAdmin):
    model = CustomerServiceProfile
    form = CustomerServiceProfileAdminForm
    list_display = [
        "department",
        "bio",
        "experience_years",
        "get_user_profile",
        "customuser_type_3",
    ]
    list_filter = [
        "department",
        "experience_years",
        "csr_profile__full_name",
        "customuser_type_3__email",
    ]
    ordering = ["experience_years"]
    fieldsets = (
        ("User Data", {"fields": ("customuser_type_3",)}),
        (
            "Customer Service Representative Details",
            {"fields": ("experience_years", "department", "bio")},
        ),
    )
    search_fields = [
        "experience_years",
        "csr_profile__full_name",
        "customuser_type_3__email",
    ]
    # Add descriptive text for the search box
    search_help_text = "experience, full name, email."
    row_id_fields = ("customuser_type_3",)
    autocomplete_fields = ["customuser_type_3"]

    def get_user_profile(self, obj):
        return str(obj.csr_profile.full_name) if obj else None

    get_user_profile.short_description = "CSR Profile Full-Name"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(
            request, obj
        )  # Get existing readonly fields
        if obj:
            readonly_fields += (
                "customuser_type_3",
            )  # Add customer_profile if obj exists
        return readonly_fields

    from django.utils.translation import gettext_lazy as _

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["search_help_text"] = self.search_help_text
        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):

        user = form.cleaned_data.get("customuser_type_3")
        department = form.cleaned_data.get("department")
        bio = form.cleaned_data.get("bio")
        experience_years = form.cleaned_data.get("experience_years")

        # If this is a new object (not being changed), we need to handle it differently
        if not change:
            # Ensure that the UserProfile exists for the selected CustomUser
            user_profile = (
                UserProfile.objects.filter(user__id=user.id).defer("user").first()
            )

            if not user_profile:
                form.add_error(
                    "customuser_type_3",
                    "The selected CustomUser does not have an associated UserProfile",
                )
                return
            try:
                # Assign values to the CustomerProfile instance
                obj.customuser_type_3 = user
                obj.csr_profile = user_profile  # Assign existing UserProfile
                obj.bio = bio
                obj.department = department
                obj.experience_years = experience_years
            except:
                logger.debug(f"Saving CustomerProfile with: {obj.__dict__}")

        # Call the superclass method to save
        super().save_model(request, obj, form, change)


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    model = ManagerProfile
    list_display = ["team", "bio", "experience_years"]
    list_filter = ["team", "bio", "experience_years"]
    ordering = ["team"]
    fieldsets = ((None, {"fields": ("team", "bio", "experience_years")}),)
    search_fields = ["team", "bio", "experience_years"]
    filter_horizontal = ()


@admin.register(AdministratorProfile)
class AdministratorProfileAdmin(admin.ModelAdmin):
    model = AdministratorProfile
    list_display = ["bio", "experience_years"]
    list_filter = ["bio", "experience_years"]
    ordering = ["experience_years"]
    fieldsets = ((None, {"fields": ("bio", "experience_years")}),)
    search_fields = ["bio", "experience_years"]
    filter_horizontal = ()
