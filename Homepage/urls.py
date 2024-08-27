from django.urls import path
from Homepage import views
from Homepage.views import (
    CustomLogoutView,
    CustomLoginView,
    SignupView,
    CustomerProfilePageView,
    SellerProfilePageView,
    HomePageView,
    CSRProfilePageView,
    ManagerProfilePageView,
    AdminProfilePageView,
    Delete_User_Account,
)
from django.contrib.auth import views as auth_views

# from axes.decorators import axes_dispatch


urlpatterns = [
    path("", HomePageView.as_view(), name="Home"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("delete-account/", Delete_User_Account.as_view(), name="delete"),
    path(
        "customer_profile_page/",
        CustomerProfilePageView.as_view(),
        name="customer_profile_page",
    ),
    path(
        "seller_profile_page/",
        SellerProfilePageView.as_view(),
        name="seller_profile_page",
    ),
    path("csr_profile_page/", CSRProfilePageView.as_view(), name="csr_profile_page"),
    path(
        "manager_profile_page/",
        ManagerProfilePageView.as_view(),
        name="manager_profile_page",
    ),
    path(
        "admin_profile_page/", AdminProfilePageView.as_view(), name="admin_profile_page"
    ),
    path("google/login/", views.google_login, name="google_login"),
    path(
        "accounts/google/login/callback/",
        views.your_callback_view,
        name="your_callback_view",
    ),
    path("google-drive/", views.read_user_document, name="google_drive"),
    path("send-email/", views.send_email, name="send_email"),
    path("send-msg/", views.send_sms, name="send_sms"),
    path("password_reset/", views.custom_password_reset, name="password_reset"),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]


# from django.urls import path
# from Homepage import views
# from Homepage.views import (
#     CustomLogoutView,
#     CustomLoginView,
#     SignupView,
#     CustomerProfilePageView,
#     SellerProfilePageView,
#     HomePageView,
#     CSRProfilePageView,
#     ManagerProfilePageView,
#     AdminProfilePageView,
#     Delete_User_Account,
# )
# from django.contrib.auth import views as auth_views

# # from axes.decorators import axes_dispatch


# urlpatterns = [
#     path("", HomePageView.as_view(), name="Home"),
#     path("signup/", SignupView.as_view(), name="signup"),
#     path("login/", CustomLoginView.as_view(), name="login"),
#     path("logout/", CustomLogoutView.as_view(), name="logout"),
#     path("delete-account/", Delete_User_Account.as_view(), name="delete"),
#     path(
#         "customer_profile_page/",
#         CustomerProfilePageView.as_view(),
#         name="customer_profile_page",
#     ),
#     path(
#         "seller_profile_page/",
#         SellerProfilePageView.as_view(),
#         name="seller_profile_page",
#     ),
#     path("csr_profile_page/", CSRProfilePageView.as_view(), name="csr_profile_page"),
#     path(
#         "manager_profile_page/",
#         ManagerProfilePageView.as_view(),
#         name="manager_profile_page",
#     ),
#     path(
#         "admin_profile_page/", AdminProfilePageView.as_view(), name="admin_profile_page"
#     ),
#     path("google/login/", views.google_login, name="google_login"),
#     path(
#         "accounts/google/login/callback/",
#         views.your_callback_view,
#         name="your_callback_view",
#     ),
#     path("google-drive/", views.read_user_document, name="google_drive"),
#     path("send-email/", views.send_email, name="send_email"),
#     path("send-msg/", views.send_sms, name="send_sms"),
#     path("password_reset/", views.custom_password_reset, name="password_reset"),
#     path(
#         "password_reset/done/",
#         auth_views.PasswordResetDoneView.as_view(
#             template_name="password_reset_done.html"
#         ),
#         name="password_reset_done",
#     ),
#     path(
#         "reset/<uidb64>/<token>/",
#         views.CustomPasswordResetConfirmView.as_view(),
#         name="password_reset_confirm",
#     ),
#     path(
#         "reset/done/",
#         auth_views.PasswordResetCompleteView.as_view(
#             template_name="password_reset_complete.html",
#         ),
#         name="password_reset_complete",
#     ),
# ]
