from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from Homepage.forms import (
    SignUpForm,
    LogInForm,
    UserProfileForm,
    SellerProfileForm,
    CustomerProfileForm,
    CustomerServiceProfileForm,
    ManagerProfileForm,
    AdministratorProfileForm,
    OTPForm,
    CustomPasswordResetForm,
    CustomUserImageForm,
    E_MailForm_For_Password_Reset,
)
from Homepage.models import (
    CustomUser,
    UserProfile,
    SellerProfile,
    CustomerProfile,
    CustomerServiceProfile,
    ManagerProfile,
    AdministratorProfile,
    CustomSocialAccount,
)
from django.http import (
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.template import loader
from django.utils.safestring import mark_safe
import json, random, stripe, requests
from django.conf import settings
from urllib.parse import urlencode
from django.urls import reverse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from twilio.rest import Client
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from i.browsing_history import your_browsing_history
from axes.decorators import axes_dispatch
from checkout.models import Payment
import logging

logger = logging.getLogger(__name__)

import cloudinary

if not settings.DEBUG:
    cloudinary.config(
        cloud_name="dh8vfw5u0",
        api_key="667912285456865",
        api_secret="QaF0OnEY-W1v2GufFKdOjo3KQm8",
        api_proxy="http://proxy.server:3128",
    )
else:
    cloudinary.config(
        cloud_name="dh8vfw5u0",
        api_key="667912285456865",
        api_secret="QaF0OnEY-W1v2GufFKdOjo3KQm8",
    )
import cloudinary.uploader
from cloudinary.uploader import upload


class HomePageView(TemplateView):
    template_name = "store.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj_list = None  # Initialize obj_list with a default value
        images = [
            "box_7",
            "box_6",
            "box_5",
            "box_3",
            "box_8",
            "box_2",
            "box_1",
            "U_N",
            "ama_zon_logo",
        ]
        cart_icon = "cart_50_50"

        image_urls = [cloudinary.CloudinaryImage(name).build_url() for name in images]
        cart_url = cloudinary.CloudinaryImage(cart_icon).build_url()
        zipped = your_browsing_history(self.request)

        context["images"] = image_urls
        context["cart_url"] = cart_url
        context["zipped"] = zipped

        if "user_id" in self.request.session:
            logger.info("user id-----------: %s", self.request.session["user_id"])
            logger.info(
                "request.user-----------: %s", self.request.user.is_authenticated
            )
        return context


class SignupView(View):
    template_name = "signup.html"
    form_class = SignUpForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        email = request.POST.get(
            "email"
        )  # Assuming the email comes from the form POST data

        existing_social_user = CustomSocialAccount.objects.filter(
            user_info__icontains=email
        ).exists()
        # Check if the user with the email already exists
        existing_user = CustomUser.objects.filter(email=email).exists()

        if existing_social_user or existing_user:
            messages.error(request, "A user with the email already exists")
            return redirect("Homepage:signup")
        else:
            form = self.form_class(request.POST)
            if form.is_valid():
                user = form.save()
                if user is not None:
                    messages.success(request, "your account is created, Please login!")
                    return redirect("Homepage:login")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

        return render(request, self.template_name, {"form": form})


class CustomLoginView(View):
    template_name = "login.html"
    form_class = LogInForm

    @method_decorator(axes_dispatch)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def start_cookie_session(self, request):
        # Start a cookie-based session by setting a value in the cookie
        self.request.session["user_id"] = self.request.user.id
        logger.info("start cookie session: %s", self.request.session["user_id"])
        # You don't need to manually set the cookie here; Django handles it internally
        # The session data will be stored in the HTTP-only cookie based on the settings

    def check_existing_cookie_session(self, request):
        # Check if the cookie-based session exists for the logged-in user
        user_id_exists = "user_id" in self.request.session
        logger.info("check existing cookie session: %s", user_id_exists)
        return user_id_exists

    def get(self, request):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect(request.GET.get("next", "/"))
        else:
            # Check for existing cookie session
            if self.check_existing_cookie_session(request):
                user_id = self.request.session.get("user_id")
                user = authenticate(request=request, user_id=user_id)
                if user is not None:
                    login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )

                    messages.success(request, "Welcome back!")
                    return redirect(request.GET.get("next", "/"))
                else:
                    messages.info(self.request, "Please fill this form to Login-in!")
                    return redirect("Homepage:login")
            else:
                form = self.form_class()
                messages.info(self.request, "Please fill this form to Login-in!")
                return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request=request, email=email, password=password)

            if user is not None:
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                self.start_cookie_session(request)
                messages.success(request, "Successfully Logged In")
                return redirect(request.GET.get("next", "/"))
            else:
                messages.error(request, "User not found: Invalid credentials")
                return redirect("Homepage:signup")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        return render(request, self.template_name, {"form": form})


def custom_password_reset(request):
    if request.method == "POST":
        email = request.POST.get("email")

        user = CustomUser.objects.filter(email=email).first()
        if user is not None:
            try:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                reset_url = request.build_absolute_uri(
                    reverse(
                        "Homepage:password_reset_confirm",
                        kwargs={"uidb64": uid, "token": token},
                    )
                )

                message = Mail(
                    from_email=settings.CLIENT_EMAIL,
                    to_emails=email,
                    subject="Reset your password",
                    html_content=f'Click the link to reset your password: <a href="{reset_url}">{reset_url}</a>',
                )
                # Initialize SendGrid API client
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                mail_json = message.get()

                # Send the email
                response = sg.client.mail.send.post(request_body=mail_json)
                logger.info(f"Email send response status: {response.status_code}")
                logger.debug(f"Email send response headers: {response.headers}")

                # Check the response status and return appropriate message
                if response.status_code == 202:
                    return HttpResponseRedirect(reverse("Homepage:password_reset_done"))
                else:
                    messages.error(request, "Fail to send E-mail, Please try again")

                    # If something went wrong, redirect to a different view or page
                    return redirect("Homepage:signup")
            except Exception as e:
                return JsonResponse({"message": f"Error: {str(e)}"}, status=500)
                # return redirect("Homepage:login")
        else:
            messages.error(request, "No user found with this email.")
            return redirect("Homepage:signup")
    else:
        form = E_MailForm_For_Password_Reset()
        return render(request, "password_reset_email.html", {"form": form})


class CustomPasswordResetConfirmView(View):
    template_name = "password_reset_confirm.html"

    def post(self, request, **kwargs):
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data["new_password1"]
            password2 = form.cleaned_data["new_password2"]

            if password1 == password2:
                uidb64 = kwargs["uidb64"]
                token = kwargs["token"]

                uid = force_str(urlsafe_base64_decode(uidb64))
                user = CustomUser.objects.filter(pk=uid).first()

                try:
                    user.set_password(password1)
                    user.save()
                    return redirect("Homepage:password_reset_complete")
                except Exception as e:
                    messages.error(request, "Something went wrong")
                    return redirect("Homepage:signup")
            else:
                return render(
                    request,
                    self.template_name,
                    {"form": form, "messages": "Passwords does match"},
                )
        else:
            return render(request, self.template_name, {"form": form})

    def get(self, request, **kwargs):
        form = CustomPasswordResetForm()
        uidb64 = kwargs["uidb64"]
        token = kwargs["token"]

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user, created = CustomUser.objects.get_or_create(pk=uid)

            if default_token_generator.check_token(user, token):
                validlink = True
                return render(
                    request, self.template_name, {"validlink": validlink, "form": form}
                )
            else:
                messages.error(request, "The URL you recieved in e-mail is not valid")
                return redirect("Homepage:signup")

        except Exception as e:
            print(e)
            return redirect("Homepage:signup")


def google_login(request):
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "email https://www.googleapis.com/auth/drive.readonly",
        "response_type": "code",
        "access_type": "offline",
    }

    url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    return redirect(url)


def your_callback_view(request):
    # Get the authorization code from the query parameters
    code = request.GET.get("code")

    # Define the parameters for token exchange
    token_params = {
        "code": code,
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    # Make a POST request to exchange the code for an access token
    token_response = requests.post(
        "https://oauth2.googleapis.com/token", data=token_params
    )

    if token_response.status_code == 200:
        with open("token_response.json", "w") as token_file:
            json.dump(token_response.json(), token_file)

        access_token = token_response.json().get("access_token")
        refresh_token = token_response.json().get("refresh_token")

        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(token_response.json())
        print("####################################################################")
        print(access_token)
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        # Use the access token to fetch user data from Google
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers=headers
        )

        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            email = user_info.get("email")

            try:
                # Check if the user already exists
                user = CustomUser.objects.get(email=email)
                try:
                    # Check if the social account already exists
                    social_account = CustomSocialAccount.objects.get(user=user)
                    # Update the access token and user info
                    social_account.access_token = access_token
                    social_account.user_info = user_info
                    social_account.refresh_token = refresh_token
                    social_account.save()

                except CustomSocialAccount.DoesNotExist:
                    # Create the social account if it doesn't exist
                    CustomSocialAccount.objects.create(
                        user=user,
                        access_token=access_token,
                        user_info=user_info,
                        refresh_token=refresh_token,
                        code=user_info,
                    )
            except CustomUser.DoesNotExist:
                # Create a new user if it doesn't exist
                user = CustomUser.objects.create(
                    email=email, username=email, user_type="SELLER"
                )
                # Create the social account for the new user
                social_account = CustomSocialAccount.objects.create(
                    user=user,
                    access_token=access_token,
                    user_info=user_info,
                    refresh_token=refresh_token,
                    code=user_info,
                )

            if "user_id" in request.session and "social_id" in request.session:
                logout(request)

            # Log the user in
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            request.session["social_id"] = social_account.id
            request.session["user_id"] = social_account.user.id
            request.session["access_token"] = social_account.access_token

            messages.success(request, "Welcome! you are logged-in")
            return redirect("Homepage:Home")
            # return redirect('Homepage:google_drive')
        else:
            return HttpError("response is not 200")
    # Handle errors or unauthorized access appropriately
    return HttpResponseNotFound("<h1>Sorry, an error occurred!</h1>")


def read_user_document(request):
    SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    # Retrieve the stored access token and refresh token for the user from your database

    user = CustomUser.objects.get(email="osama.aslam.86004@gmail.com")
    social_account = CustomSocialAccount.objects.get(user=user)

    access_token = social_account.access_token
    refresh_token = social_account.refresh_token

    # Build credentials using the stored tokens
    credentials = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
        scopes=SCOPES,
    )

    try:
        # Build the Google Drive service using the credentials
        drive_service = build("drive", "v3", credentials=credentials)

        # Retrieve a list of files in the user's Drive
        response = drive_service.files().list().execute()

        file_names = []
        # Process the response
        files = response.get("files", [])
        if files:
            for file in files:
                file_names.append(file.get("name"))
                print(f"File Name: {file.get('name')}")
                files_info = ", ".join(file_names)
            return HttpResponse(f"Files retrieved successfully: {files_info}")
        else:
            return HttpResponse("No files found.")
    except HttpError as e:
        print(f"Error accessing Google Drive: {e}")
        # Handle the error appropriately
        return HttpResponse("Error accessing Google Drive")


class CustomLogoutView(View, SuccessMessageMixin):
    success_message = "You have been logged out successfully"

    def get(self, request):
        try:
            if request.user.is_authenticated:
                if "user_id" in request.session:
                    user_id = request.session.get("user_id")
                    if not CustomSocialAccount.objects.filter(
                        id=user_id, user=request.user
                    ).exists():
                        logout(request)
                        messages.success(request, self.success_message)
                    else:
                        social_user = CustomSocialAccount.objects.get(id=user_id)
                        if self.google_logout(request, social_user.access_token):
                            messages.success(request, self.success_message)
                            logout(request)

                        else:
                            messages.info(request, "Unable to log you out from Google.")
                            # try:
                            social_user.access_token = ""
                            social_user.refresh_token = ""
                            social_user.save()
                            logout(request)  # added 6/16/2024

                        # except Exception as e:
                        #     logger.exception("Error saving social user: %s", e)
                        #     messages.error(request, "{e}")
                else:
                    messages.error(request, "You are not logged in. Please login!")
                    logout(request)
            else:
                messages.error(request, "You are not logged in. Please login!")
                logout(request)
        except Exception as e:
            logger.exception("Error during logout: %s", e)
            messages.error(request, "An error occurred during logout.")
        return redirect("Homepage:login")

    def google_logout(self, request, access_token):
        revoke_token_url = "https://oauth2.googleapis.com/revoke"
        params = {"token": access_token}

        try:
            revoke_response = requests.post(revoke_token_url, params=params)
            revoke_response.raise_for_status()
            logger.info("successfully Google logout: %s", revoke_response)
            return True
        except requests.exceptions.RequestException as e:
            logger.error("Google logout failed: %s", e)
            return False


def custom_csrf_failure(request, reason=""):
    # Your custom logic for handling CSRF failures
    # Mark the reason as safe to render HTML
    reason_message = mark_safe(reason)
    context = {
        "reason": reason_message
    }  # Pass any additional context data needed for the template
    template = loader.get_template("custom_csrf_failure.html")
    return HttpResponseForbidden(template.render(context, request))


@method_decorator(login_required, name="dispatch")
class CustomerProfilePageView(PermissionRequiredMixin, TemplateView):
    user_profile_form_class = UserProfileForm
    customer_profile_form_class = CustomerProfileForm
    permission_required = [
        "Homepage.customer_create_profile",
        "Homepage.customer_edit_profile",
        "Homepage.customer_delete_profile",
    ]
    template_name = "customer_profile_page.html"

    # inherited from PermissionRequiredMixin
    def handle_no_permission(self):
        user_email = (
            self.request.user.email if self.request.user.is_authenticated else "unknown"
        )
        user_permission = "create and edit CUSTOMER profile"
        return render(
            self.request,
            "permission_denied.html",
            {"user_email": user_email, "user_permission": user_permission},
        )

    def redirect_to_login(self, request):
        messages.error(request, "Your are not Logged-in, Please Log-in!")
        return redirect("/login/")

    def display_customer_user_type_permissions(self, request):
        social_id = request.session.get("social_id")

        # Check if user is not logged in via google account
        if "user_id" in request.session and not "social_id" in request.session:
            user = self.request.user
            user_permissions = user.get_all_permissions()
            clean_permissions = {
                permission.split(".")[1] for permission in user_permissions
            }
            return clean_permissions
        else:
            try:
                social_user = CustomSocialAccount.objects.filter(id=social_id).first()
                # model level permissions
                content_type = ContentType.objects.get_for_model(CustomSocialAccount)
                permissions = Permission.objects.filter(
                    content_type=content_type,
                )

                user = request.user
                # get all permission for user=social_user.user except Model level
                user_permissions = user.get_all_permissions()
                clean_permissions = {
                    permission.split(".")[1] for permission in user_permissions
                }
                # update the user permission with content type permissions
                clean_permissions.update(
                    {permission.name for permission in permissions}
                )

                return clean_permissions

            except CustomSocialAccount.DoesNotExist:
                messages.error(request, "Social user does not exist")
                return {}

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logger.info(
                "check if user is authenticated %s", request.user.is_authenticated
            )
            return super().get(request, *args, **kwargs)

        else:
            return self.redirect_to_login(request)

    def post(self, request):
        if not request.user.is_authenticated:
            return self.redirect_to_login(request)

        current_user = get_object_or_404(CustomUser, id=request.user.id)

        image_form = CustomUserImageForm(instance=current_user)
        user_profile = UserProfile.objects.get(user=current_user)
        customer_profile = CustomerProfile.objects.get(customer_profile=user_profile)

        user_profile_form = self.user_profile_form_class(
            request.POST, instance=user_profile
        )
        customer_profile_form = self.customer_profile_form_class(
            request.POST, instance=customer_profile
        )

        image_form = CustomUserImageForm(request.POST, request.FILES)

        if (
            user_profile_form.is_valid()
            and customer_profile_form.is_valid()
            and image_form.is_valid()
        ):
            user_form = user_profile_form.save(commit=False)
            customer_form = customer_profile_form.save(commit=False)
            transformation_options = {
                "width": 75,
                "height": 75,
                "crop": "fill",
                "gravity": "face",
                "effect": "auto_contrast",
            }
            try:
                image_data = upload(
                    # be careful using form.cleaned_data["image"] require "file" as positional arg
                    # self.request.FILES does not need "file" as positional arg
                    # one can set the any name for this arg
                    # form.is_valid() automatically check if uploaded file is an image file or other format
                    file=image_form.cleaned_data["image"],
                    transformation=transformation_options,
                    resource_type="image",
                )

                self.request.user.image = image_data["url"]
                self.request.user.save()

                user_form = user_profile_form.save()
                customer_form = customer_profile_form.save()
                messages.success(request, "Your profile is successfully updated!")
                return redirect(request.GET.get("next", "/"))
            except:
                messages.error(request, "Image upload failed")

        return render(
            request,
            self.template_name,
            {
                "user_profile_form": user_profile_form,
                "customer_profile_form": customer_profile_form,
                "image_form": image_form,
            },
        )

    # Method to prepare context data for the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        image = self.request.user.image
        # Fetch or create user and customer profiles
        custom_user, created = CustomUser.objects.get_or_create(id=self.request.user.id)
        user_profile, created_user_profile = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        (
            customer_profile,
            created_customer_profile,
        ) = CustomerProfile.objects.get_or_create(
            customer_profile=user_profile, customuser_type_1=self.request.user
        )

        # Create forms instances and add to context
        image_form = CustomUserImageForm(instance=custom_user)
        user_profile_form = UserProfileForm(instance=user_profile)
        customer_profile_form = CustomerProfileForm(instance=customer_profile)

        clean_permissions = self.display_customer_user_type_permissions(self.request)

        context["user_profile_form"] = user_profile_form
        context["customer_profile_form"] = customer_profile_form
        context["clean_permissions"] = clean_permissions
        context["image_form"] = image_form
        context["image"] = image

        return context


@method_decorator(login_required, name="dispatch")
class SellerProfilePageView(PermissionRequiredMixin, TemplateView):
    template_name = "seller_profile_page.html"
    permission_required = [
        "Homepage.seller_edit_profile",
        "Homepage.seller_create_profile",
        "Homepage.seller_delete_profile",
    ]

    # inherited from PermissionRequiredMixin
    def handle_no_permission(self):
        user_email = (
            self.request.user.email if self.request.user.is_authenticated else "unknown"
        )
        user_permission = "create and edit SELLER profile"
        return render(
            self.request,
            "permission_denied.html",
            {"user_email": user_email, "user_permission": user_permission},
        )

    def redirect_to_login(self, request):
        messages.error(request, "Your are not Logged-in, Please Log-in!")
        return redirect("/login/")

    def display_seller_user_type_permissions(self, request):
        social_id = request.session.get("social_id")

        if "user_id" in request.session and not "social_id" in request.session:
            user = self.request.user
            user_permissions = user.get_all_permissions()
            clean_permissions = {
                permission.split(".")[1] for permission in user_permissions
            }
            return clean_permissions
        else:
            try:
                social_user = CustomSocialAccount.objects.filter(id=social_id).first()
                # model level permissions
                content_type = ContentType.objects.get_for_model(CustomSocialAccount)
                permissions = Permission.objects.filter(
                    content_type=content_type,
                )

                user = request.user
                # get all permission for user=social_user.user except Model level
                user_permissions = user.get_all_permissions()
                clean_permissions = {
                    permission.split(".")[1] for permission in user_permissions
                }
                # update the user permission with content type permissions
                clean_permissions.update(
                    {permission.name for permission in permissions}
                )

                return clean_permissions

            except CustomSocialAccount.DoesNotExist:
                messages.error(request, "Social user does not exist")
                return {}

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.redirect_to_login(request)

        return super().get(request, *args, **kwargs)

    def post(self, request):
        if not request.user.is_authenticated:
            return self.redirect_to_login(request)

        current_user = get_object_or_404(CustomUser, id=request.user.id)

        image_form = CustomUserImageForm(instance=current_user)
        user_profile = UserProfile.objects.get(user=current_user)
        seller_profile = SellerProfile.objects.get(seller_profile=user_profile)

        user_profile_form = UserProfileForm(request.POST, instance=user_profile)
        seller_profile_form = SellerProfileForm(request.POST, instance=seller_profile)

        image_form = CustomUserImageForm(request.POST, request.FILES)

        if (
            user_profile_form.is_valid()
            and seller_profile_form.is_valid()
            and image_form.is_valid()
        ):
            user_form = user_profile_form.save(commit=False)
            seller_form = seller_profile_form.save(commit=False)

            transformation_options = {
                "width": 75,
                "height": 75,
                "crop": "fill",
                "gravity": "face",
                "effect": "auto_contrast",
            }
            try:
                image_data = upload(
                    # be careful using form.cleaned_data["image"] require "file" as positional arg
                    # self.request.FILES does not need "file" as positional arg
                    # one can set the any name for this arg
                    file=image_form.cleaned_data["image"],
                    transformation=transformation_options,
                    resource_type="image",
                )

                self.request.user.image = image_data["url"]
                self.request.user.save()
                user_form.save()
                seller_form.save()

                messages.success(request, "Your profile is successfully updated!")
                return redirect(request.GET.get("next", "/"))
            except Exception as e:
                messages.error(request, "Image upload failed")

        return render(
            request,
            self.template_name,
            {
                "user_profile_form": user_profile_form,
                "seller_profile_form": seller_profile_form,
                "image_form": image_form,
            },
        )

    # Method to prepare context data for the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        image = self.request.user.image
        # Fetch or create user and customer profiles
        # custom_user == self.request.user
        custom_user, created = CustomUser.objects.get_or_create(id=self.request.user.id)
        user_profile, created_user_profile = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        seller_profile, created_customer_profile = SellerProfile.objects.get_or_create(
            seller_profile=user_profile, customuser_type_2=self.request.user
        )

        # Create forms instances and add to context
        image_form = CustomUserImageForm(instance=custom_user)
        user_profile_form = UserProfileForm(instance=user_profile)
        seller_profile_form = SellerProfileForm(instance=seller_profile)

        clean_permissions = self.display_seller_user_type_permissions(self.request)

        context["user_profile_form"] = user_profile_form
        context["seller_profile_form"] = seller_profile_form
        context["clean_permissions"] = clean_permissions
        context["image_form"] = image_form
        context["image"] = image
        context["user_id"] = self.request.user.id

        return context


@method_decorator(login_required, name="dispatch")
class CSRProfilePageView(PermissionRequiredMixin, TemplateView):
    template_name = "csr_profile_page.html"
    permission_required = [
        "Homepage.csr_edit_profile",
        "Homepage.csr_create_profile",
        "Homepage.csr_delete_profile",
    ]

    # inherited from PermissionRequiredMixin
    def handle_no_permission(self):
        user_email = (
            self.request.user.email if self.request.user.is_authenticated else "unknown"
        )
        user_permission = "create and edit CUSTOMER REPRESENTATIVE profile"
        return render(
            self.request,
            "permission_denied.html",
            {"user_email": user_email, "user_permission": user_permission},
        )

    def redirect_to_login(self, request):
        messages.error(request, "Your are not Logged-in, Please Log-in!")
        return redirect("/login/")

    def display_csr_user_type_permissions(self, request):
        social_id = request.session.get("social_id")

        if "user_id" in request.session and not "social_id" in request.session:
            user = self.request.user
            user_permissions = user.get_all_permissions()
            clean_permissions = {
                permission.split(".")[1] for permission in user_permissions
            }
            return clean_permissions
        else:
            try:
                social_user = CustomSocialAccount.objects.filter(id=social_id).first()
                # model level permissions
                content_type = ContentType.objects.get_for_model(CustomSocialAccount)
                permissions = Permission.objects.filter(
                    content_type=content_type,
                )

                user = request.user
                # get all permission for user=social_user.user except Model level
                user_permissions = user.get_all_permissions()
                clean_permissions = {
                    permission.split(".")[1] for permission in user_permissions
                }
                # update the user permission with content type permissions
                clean_permissions.update(
                    {permission.name for permission in permissions}
                )

                return clean_permissions

            except CustomSocialAccount.DoesNotExist:
                messages.error(request, "Social user does not exist")
                return {}

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.redirect_to_login(request)

        return super().get(request, *args, **kwargs)

    def post(self, request):
        if not request.user.is_authenticated:
            return self.redirect_to_login(request)

        current_user = get_object_or_404(CustomUser, id=request.user.id)

        image_form = CustomUserImageForm(instance=current_user)
        user_profile = UserProfile.objects.get(user=current_user)
        csr_profile = CustomerServiceProfile.objects.get(csr_profile=user_profile)

        user_profile_form = UserProfileForm(request.POST, instance=user_profile)
        csr_profile_form = CustomerServiceProfileForm(
            request.POST, instance=csr_profile
        )
        image_form = CustomUserImageForm(request.POST, request.FILES)

        if (
            user_profile_form.is_valid()
            and csr_profile_form.is_valid()
            and image_form.is_valid()
        ):
            user_form = user_profile_form.save(commit=False)
            csr_form = csr_profile_form.save(commit=False)
            transformation_options = {
                "width": 75,
                "height": 75,
                "crop": "fill",
                "gravity": "face",
                "effect": "auto_contrast",
            }
            try:
                image_data = upload(
                    # be careful using form.cleaned_data["image"] require "file" as positional arg
                    # self.request.FILES does not need "file" as positional arg
                    # one can set the any name for this arg
                    file=image_form.cleaned_data["image"],
                    transformation=transformation_options,
                    resource_type="image",
                )

                self.request.user.image = image_data["url"]
                self.request.user.save()

                user_form.save()
                csr_form.save()
                messages.success(request, "Your profile is successfully updated!")
                return redirect(request.GET.get("next", "/"))
            except:
                messages.error(request, "Image upload failed")

        return render(
            request,
            self.template_name,
            {
                "user_profile_form": user_profile_form,
                "csr_profile_form": csr_profile_form,
                "image_form": image_form,
            },
        )

    # Method to prepare context data for the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        image = self.request.user.image
        # Fetch or create user and customer profiles
        # custom_user == self.request.user
        custom_user, created = CustomUser.objects.get_or_create(id=self.request.user.id)
        user_profile, created_user_profile = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        (
            csr_profile,
            created_customer_profile,
        ) = CustomerServiceProfile.objects.get_or_create(
            csr_profile=user_profile, customuser_type_3=self.request.user
        )

        # Create forms instances and add to context
        image_form = CustomUserImageForm(instance=custom_user)
        user_profile_form = UserProfileForm(instance=user_profile)
        csr_profile_form = CustomerServiceProfileForm(instance=csr_profile)

        clean_permissions = self.display_csr_user_type_permissions(self.request)

        context["user_profile_form"] = user_profile_form
        context["csr_profile_form"] = csr_profile_form
        context["clean_permissions"] = clean_permissions
        context["image_form"] = image_form
        context["image"] = image

        return context


@method_decorator(login_required, name="dispatch")
class ManagerProfilePageView(PermissionRequiredMixin, TemplateView):
    template_name = "manager_profile_page.html"
    permission_required = [
        "Homepage.manager_edit_profile",
        "Homepage.manager_create_profile",
        "Homepage.manager_delete_profile",
    ]

    # inherited from PermissionRequiredMixin
    def handle_no_permission(self):
        user_email = (
            self.request.user.email if self.request.user.is_authenticated else "unknown"
        )
        user_permission = "create and edit MANAGER profile"
        return render(
            self.request,
            "permission_denied.html",
            {"user_email": user_email, "user_permission": user_permission},
        )

    def redirect_to_login(self, request):
        messages.error(request, "Your are not Logged-in, Please Log-in!")
        return redirect("/login/")

    def display_manager_user_type_permissions(self, request):
        social_id = request.session.get("social_id")

        if "user_id" in request.session and not "social_id" in request.session:
            user = self.request.user
            user_permissions = user.get_all_permissions()
            clean_permissions = {
                permission.split(".")[1] for permission in user_permissions
            }
            return clean_permissions
        else:
            try:
                social_user = CustomSocialAccount.objects.filter(id=social_id).first()
                # model level permissions
                content_type = ContentType.objects.get_for_model(CustomSocialAccount)
                permissions = Permission.objects.filter(
                    content_type=content_type,
                )

                user = request.user
                # get all permission for user=social_user.user except Model level
                user_permissions = user.get_all_permissions()
                clean_permissions = {
                    permission.split(".")[1] for permission in user_permissions
                }
                # update the user permission with content type permissions
                clean_permissions.update(
                    {permission.name for permission in permissions}
                )

                return clean_permissions

            except CustomSocialAccount.DoesNotExist:
                messages.error(request, "Social user does not exist")
                return {}

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.redirect_to_login(request)

        return super().get(request, *args, **kwargs)

    def post(self, request):
        if not request.user.is_authenticated:
            return self.redirect_to_login(request)

        current_user = get_object_or_404(CustomUser, id=request.user.id)

        image_form = CustomUserImageForm(instance=current_user)
        user_profile = UserProfile.objects.get(user=current_user)
        manager_profile = ManagerProfile.objects.get(manager_profile=user_profile)

        user_profile_form = UserProfileForm(request.POST, instance=user_profile)
        manager_profile_form = ManagerProfileForm(
            request.POST, instance=manager_profile
        )
        image_form = CustomUserImageForm(request.POST, request.FILES)
        if (
            user_profile_form.is_valid()
            and manager_profile_form.is_valid()
            and image_form.is_valid()
        ):
            user_form = user_profile_form.save(commit=False)
            manager_form = manager_profile_form.save(commit=False)
            transformation_options = {
                "width": 75,
                "height": 75,
                "crop": "fill",
                "gravity": "face",
                "effect": "auto_contrast",
            }
            try:
                image_data = upload(
                    # be careful using form.cleaned_data["image"] require "file" as positional arg
                    # self.request.FILES does not need "file" as positional arg
                    # one can set the any name for this arg
                    file=image_form.cleaned_data["image"],
                    transformation=transformation_options,
                    resource_type="image",
                )

                self.request.user.image = image_data["url"]
                self.request.user.save()

                user_form.save()
                manager_form.save()
                messages.success(request, "Your profile is successfully updated!")
                return redirect(request.GET.get("next", "/"))
            except:
                messages.error(request, "Image upload failed")

        return render(
            request,
            self.template_name,
            {
                "user_profile_form": user_profile_form,
                "manager_profile_form": manager_profile_form,
                "image_form": image_form,
            },
        )

    # Method to prepare context data for the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch or create user and customer profiles
        # custom_user == self.request.user
        custom_user, created = CustomUser.objects.get_or_create(id=self.request.user.id)
        user_profile, created_user_profile = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        (
            manager_profile,
            created_customer_profile,
        ) = ManagerProfile.objects.get_or_create(
            manager_profile=user_profile, customuser_type_4=self.request.user
        )

        # Create forms instances and add to context
        image_form = CustomUserImageForm(instance=custom_user)
        user_profile_form = UserProfileForm(instance=user_profile)
        manager_profile_form = ManagerProfileForm(instance=manager_profile)

        clean_permissions = self.display_manager_user_type_permissions(self.request)

        context["user_profile_form"] = user_profile_form
        context["manager_profile_form"] = manager_profile_form
        context["clean_permissions"] = clean_permissions
        context["image_form"] = image_form
        context["image"] = self.request.user.image

        return context


class AdminProfilePageView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url = "/login/"
    permission_required = [
        "Homepage.admin_edit_seller_profile",
        "Homepage.admin_delete_csr_profile",
    ]
    template_name = "admin_profile_page.html"

    # inherited from PermissionRequiredMixin
    def handle_no_permission(self):
        user_email = (
            self.request.user.email if self.request.user.is_authenticated else "unknown"
        )
        user_permission = "create and edit ADMINISTRATOR profile"
        return render(
            self.request,
            "permission_denied.html",
            {"user_email": user_email, "user_permission": user_permission},
        )

    def display_manager_user_type_permissions(self, request):
        social_id = request.session.get("social_id")

        if "user_id" in request.session and not "social_id" in request.session:
            user = self.request.user
            user_permissions = user.get_all_permissions()
            clean_permissions = {
                permission.split(".")[1] for permission in user_permissions
            }
            return clean_permissions
        else:
            try:
                social_user = CustomSocialAccount.objects.filter(id=social_id).first()
                # model level permissions
                content_type = ContentType.objects.get_for_model(CustomSocialAccount)
                permissions = Permission.objects.filter(
                    content_type=content_type,
                )

                user = request.user
                # get all permission for user=social_user.user except Model level
                user_permissions = user.get_all_permissions()
                clean_permissions = {
                    permission.split(".")[1] for permission in user_permissions
                }
                # update the user permission with content type permissions
                clean_permissions.update(
                    {permission.name for permission in permissions}
                )

                return clean_permissions

            except CustomSocialAccount.DoesNotExist:
                messages.error(request, "Social user does not exist")
                return {}

    def get(self, request):
        current_user = get_object_or_404(CustomUser, id=self.request.user.id)

        user_profile, created_user_profile = UserProfile.objects.get_or_create(
            user=current_user
        )

        (
            Admin_profile,
            created_customer_profile,
        ) = AdministratorProfile.objects.get_or_create(
            admin_profile=user_profile, user=current_user
        )

        image_form = CustomUserImageForm(instance=current_user)
        user_profile_form = UserProfileForm(instance=user_profile)
        admin_profile_form = AdministratorProfileForm(instance=Admin_profile)

        clean_permissions = self.display_manager_user_type_permissions(self.request)

        return render(
            request,
            self.template_name,
            {
                "user_profile_form": user_profile_form,
                "admin_profile_form": admin_profile_form,
                "clean_permissions": clean_permissions,
                "image_form": image_form,
                "image": self.request.user.image,
            },
        )

    def post(self, request):
        user_profile, created_user_profile = UserProfile.objects.get_or_create(
            user=self.request.user
        )

        (
            Admin_profile,
            created_customer_profile,
        ) = AdministratorProfile.objects.get_or_create(
            admin_profile=user_profile, user=self.request.user
        )

        user_profile_form = UserProfileForm(request.POST, instance=user_profile)
        admin_profile_form = AdministratorProfileForm(
            request.POST, instance=Admin_profile
        )

        image_form = CustomUserImageForm(request.POST, request.FILES)
        if (
            user_profile_form.is_valid()
            and admin_profile_form.is_valid()
            and image_form.is_valid()
        ):
            user_form = user_profile_form.save(commit=False)
            admin_form = admin_profile_form.save(commit=False)
            transformation_options = {
                "width": 75,
                "height": 75,
                "crop": "fill",
                "gravity": "face",
                "effect": "auto_contrast",
            }
            try:
                image_data = upload(
                    # be careful using form.cleaned_data["image"] require "file" as positional arg
                    # self.request.FILES does not need "file" as positional arg
                    # one can set the any name for this arg
                    file=image_form.cleaned_data["image"],
                    transformation=transformation_options,
                    resource_type="image",
                )

                self.request.user.image = image_data["url"]
                self.request.user.save()

                user_form.save()
                admin_form.save()
                messages.success(request, "Your profile is successfully updated!")
                return redirect("/")
            except:
                messages.error(request, "Image upload failed")

        return render(
            request,
            self.template_name,
            {
                "user_profile_form": user_profile_form,
                "admin_profile_form": admin_profile_form,
                "image_form": image_form,
            },
        )


def send_email(request):
    # Your dynamic data to be passed to the template
    dynamic_data = {
        "customerName": "John Doe",
        "orderDate": "04/12/23",
        "customerEmail": "osama.aslam.86004@gmail.com",
        # Add more dynamic data as needed
    }

    # Your SendGrid template ID
    template_id = settings.TEMPLATE_ID

    # Prepare the email content using the SendGrid template
    message = Mail(
        from_email=settings.CLIENT_EMAIL,  # Update with your sender email
        to_emails=settings.CLIENT_EMAIL,  # Update with recipient email
    )
    message.template_id = template_id
    message.dynamic_template_data = dynamic_data

    try:
        # Initialize SendGrid API client
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        # Send the email
        response = sg.send(message)

        # Check the response status and return appropriate message
        if response.status_code == 202:
            return JsonResponse({"message": "Email sent successfully"})
        else:
            return JsonResponse({"message": "Failed to send email"}, status=500)
    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=500)


def generate_otp():
    # Generate a 6-digit OTP
    return str(random.randint(100000, 999999))


def send_sms(request):
    if request.method == "POST":
        otp_form = OTPForm(request.POST)
        form = E_MailForm_For_Password_Reset(request.POST)

        generated_otp = request.session.get("generated_otp")

        if otp_form.is_valid() and otp_form.cleaned_data["otp"] is not None:
            user_entered_otp = otp_form.cleaned_data["otp"]

            if str(generated_otp) == str(user_entered_otp):
                if "user_id" in request.session:
                    user_id = request.session.get("user_id")
                    user = CustomUser.objects.get(id=user_id)
                    authenticate(request=request, user=user)
                    login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )
                    messages.success(request, "Successfully Logged In")
                    return redirect(request.GET.get("next", "/"))
                else:
                    email = request.session.get("email")
                    user = CustomUser.objects.get(email=email)
                    authenticate(request=request, user=user)
                    login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )
                    request.session["user_id"] = user.id
                    messages.success(request, "Successfully Logged In")
                    return redirect(request.GET.get("next", "/"))
            else:
                messages.error(request, "You entered Incorrect OTP")
                return render(
                    request,
                    "otp.html",
                    {"form": otp_form},
                )
        else:
            if form.is_valid():
                user_entered_email = form.cleaned_data["email"]
                request.session["email"] = user_entered_email
                print(f"email___________{request.session['email']}")

                user = CustomUser.objects.get(email=user_entered_email)
                user_profile = UserProfile.objects.get(user=user)

                print(f"phone_number_________________{user_profile.phone_number}")
                if user_profile.phone_number:
                    generated_otp = generate_otp()
                    request.session["generated_otp"] = generated_otp
                    phone_number = user_profile.phone_number
                    print(f"generated_otp___________{request.session['generated_otp']}")

                    if helper_function(generated_otp, phone_number):
                        form = OTPForm
                        messages.success(
                            request, "An OTP has been sent to your mobile number"
                        )
                        return render(request, "otp.html", {"form": form})
                    else:
                        messages.error(
                            request, "Failed to send SMS, Please log-in again"
                        )
                        return redirect("Homepage:login")
                else:
                    messages.warning(
                        request,
                        "Your Phone Number does not exist in database, so you have to recover your password with e-mail verification method",
                    )
                    return redirect("Homepage:password_reset")
            else:
                form = E_MailForm_For_Password_Reset()
                return render(request, "password_reset_email.html", {"form": form})
    else:
        try:
            if "user_id" in request.session:
                user_id = request.session.get("user_id")

                user = CustomUser.objects.get(id=user_id)
                user_profile = UserProfile.objects.get(user=user)
                if user_profile.phone_number:
                    phone_number = user_profile.phone_number
                    generated_otp = generate_otp()
                    request.session["generated_otp"] = generated_otp

                    print(f"generated_otp___________{request.session['generate_otp']}")
                    print(f"phone_number_________________{user_profile.phone_number}")

                    if helper_function(generated_otp, phone_number):

                        form = OTPForm
                        messages.success(
                            request, "An OTP has been sent to your mobile number"
                        )
                        return render(request, "otp.html", {"form": form})
                    else:
                        messages.error(
                            request, "Failed to send SMS, Please log-in again"
                        )
                        return redirect("Homepage:login")
                else:
                    messages.warning(
                        request,
                        "Your Phone Number does not exist in database, so you have to recover your password with e-mail verification method",
                    )
                    return redirect("Homepage:password_reset")
            else:
                form = E_MailForm_For_Password_Reset()
                return render(request, "password_reset_email.html", {"form": form})
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)


def helper_function(generated_otp, phone_number):
    import requests

    # Twilio API endpoint
    endpoint = f"https://api.twilio.com/2010-04-01/Accounts/{settings.ACCOUNT_SID}/Messages.json"

    # Construct the request payload
    payload = {
        "From": settings.FROM_,
        "To": str(phone_number),  # otherwise 'PhoneNumber' object is not iterable
        "Body": f"Your OTP is: {generated_otp}",
    }

    # HTTP Basic Authentication credentials
    auth = (settings.ACCOUNT_SID, settings.AUTH_TOKEN)

    # Send HTTP POST request to Twilio
    # response = requests.post(endpoint, data=payload, auth=auth, verify=False)
    response = requests.post(endpoint, data=payload, auth=auth)

    # Check if request was successful
    if response.status_code == 201:
        return True
    else:
        return False

    # # message body
    # message_body = f"Your OTP is: {generated_otp}"

    # account_sid = settings.ACCOUNT_SID
    # auth_token = settings.AUTH_TOKEN

    # client = Client(account_sid, auth_token)

    # message = client.messages.create(
    #     from_=settings.FROM_, body=message_body, to=str(phone_number)
    # )

    # if message.sid:
    #     return True
    # else:
    #     return False


class Delete_User_Account(View):
    def delete_user_stripe_account(self):
        user_id = self.request.session["user_id"]
        payment = Payment.objects.filter(user__id=user_id)
        if payment:
            customer_id = payment[0].stripe_customer_id
            try:
                delete_stripe_customer = stripe.Customer.delete(customer_id)
                return delete_stripe_customer["deleted"]
            except Exception as e:
                return JsonResponse({"error": str(e)})
        else:
            return False

    def get(self, *args, **kwargs):
        if "user_id" in self.request.session:
            user_id = self.request.session["user_id"]
            user = CustomUser.objects.filter(id=user_id)
            if user:
                if self.request.user.is_authenticated:
                    if self.delete_user_stripe_account():
                        logout(self.request)
                        user[0].delete()
                        messages.info(self.request, "Your account is deleted!")
                        return redirect("Homepage:Home")
                    else:
                        logout(self.request)
                        user[0].delete()
                        messages.info(self.request, "Your account is deleted!")
                        return redirect("Homepage:Home")
                else:
                    return redirect("Homepage:login")
            else:
                response = redirect("Homepage:Home")
                response.delete_cookie("sessionid")
                return response
        else:
            messages.info(self.request, "please Log-in to delete your account")
            return redirect("Homepage:login")
