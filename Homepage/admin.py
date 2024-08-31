from django.contrib import admin
from django import forms
from Homepage.models import (UserProfile, CustomerProfile, CustomerServiceProfile, ManagerProfile, SellerProfile,
                             AdministratorProfile, CustomUser)



class CustomUserAdmin(admin.ModelAdmin):
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES)
    model = CustomUser
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'user_type', 'date_joined', 'last_login']
    list_filter = ['username', 'user_type']
    ordering = ['username', ]
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Additional Information', {
            'fields': ('first_name', 'last_name', 'is_staff', 'is_superuser', 'user_type', 'date_joined', 'last_login'),
        }),
    )
    search_fields = ['email', 'username', 'first_name', 'last_name']
    filter_horizontal = ()


    # Customize the add view
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'is_staff', 'user_type'),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Set the user's type based on the field in the form (e.g., user_type)
        obj.user_type = form.cleaned_data.get('user_type', 'customer')
        super().save_model(request, obj, form, change)

admin.site.register(CustomUser, CustomUserAdmin)



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [  'full_name', 'age', 'gender', 'phone_number', 'city', 'country', 'postal_code']
    list_filter = ['gender', 'city', 'country']
    search_fields = ['user__username', 'full_name', 'phone_number']
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ( 'full_name', 'age', 'gender', 'phone_number')
        }),
        ('Location', {
            'fields': ('city', 'country', 'postal_code')
        }),
    )

    read_only = ['user',]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('phone_number',)  # Make 'phone_number' read-only
        return self.readonly_fields

    def get_exclude(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('user',)  # Hide 'user' field
        return ()


class CustomerAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ['shipping_address', 'wishlist']
    list_filter = ['shipping_address' ]
    ordering = ['wishlist',]
    fieldsets = (
        (None, {
            'fields': ('shipping_address', 'wishlist')
        }),
    )
    search_fields = ['shipping_address', 'wishlist']
    filter_horizontal = ()
admin.site.register(CustomerProfile, CustomerAdmin)


class SellerAdmin(admin.ModelAdmin):
    model = SellerProfile
    list_display = ['address']
    list_filter = ['address' ]
    ordering = ['address']
    fieldsets = (
    (None, {
        'fields': ('address',)  
    }),
)
    search_fields = ['address',]
    filter_horizontal = ()
admin.site.register(SellerProfile, SellerAdmin)


class CustomerServiceProfileAdmin(admin.ModelAdmin):
    model = CustomerServiceProfile
    list_display = ['department', 'bio', 'experience_years']
    list_filter = ['department', 'bio', 'experience_years' ]
    ordering = ['department']
    fieldsets = (
        (None, {
            'fields': ('department', 'bio', 'experience_years')
        }),
    )
    search_fields = ['department', 'bio', 'experience_years']
    filter_horizontal = ()
admin.site.register(CustomerServiceProfile, CustomerServiceProfileAdmin)


class ManagerProfileAdmin(admin.ModelAdmin):
    model = ManagerProfile
    list_display = ['team',  'bio', 'experience_years']
    list_filter = ['team', 'bio', 'experience_years' ]
    ordering = ['team']
    fieldsets = (
        (None, {
            'fields': ('team', 'bio', 'experience_years')
        }),
    )
    search_fields = ['team',  'bio', 'experience_years']
    filter_horizontal = ()
admin.site.register(ManagerProfile, ManagerProfileAdmin)

class AdministratorProfileAdmin(admin.ModelAdmin):
    model = AdministratorProfile
    list_display = [ 'bio', 'experience_years']
    list_filter = [ 'bio', 'experience_years' ]
    ordering = ['experience_years']
    fieldsets = (
        (None, {
            'fields': ('bio', 'experience_years')
        }),
    )
    search_fields = [ 'bio', 'experience_years']
    filter_horizontal = ()
admin.site.register(AdministratorProfile, AdministratorProfileAdmin)
