"""
Django settings for iii project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from re import T

from decouple import config

# Twilio API
TEMPLATES_ID = config("template_id")
ACCOUNT_SID = config("account_sid")
AUTH_TOKEN = config("auth_token")
FROM_ = config("from_")


# Sendgrid Email API
SENDGRID_API_KEY = config("SENDGRID_API_KEY")
CLIENT_EMAIL = config("client_email_address")
TEMPLATE_ID = config("template_id")
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_SANDBOX_MODE_IN_DEBUG = True
SENDGRID_ECHO_TO_STDOUT = True

# stripe API keys
PAYMENT_HOST = "https://django-e-commrace.vercel.app/checkout/stripe_webhook"
PAYMENT_USES_SSL = True
PUBLISHABLE_KEY = config("Publishable_key")
STRIPE_SECRET_KEY = config("Secret_Key")
ENDPOINT_SIGNING_SECRET = config("STRIPE_SIGNING_SECRET")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
if DEBUG:
    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
        "diverse-intense-whippet.ngrok-free.app",
    ]
else:
    ALLOWED_HOSTS = ["osama11111.pythonanywhere.com"]

# Application definition

INSTALLED_APPS = [
    "grappelli",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "i",
    "Homepage",
    "blog",
    "cart",
    "checkout",
    "cv_api",
    "django_extensions",
    # "django_htmx",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_bootstrap5",
    "cloudinary_storage",
    "cloudinary",
    "ckeditor",
    "book_",
    "django_twilio",
    "axes",
    "phonenumber_field",
    "django_countries",
    "compressor",
]

SITE_ID = 1

MIDDLEWARE = [
    "csp.middleware.CSPMiddleware",  # CSP header
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",  # Add GZipMiddleware here
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # comment it if X-FRAME OPTION is None
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "iii.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    }
]
WSGI_APPLICATION = "iii.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": config("POSTGRES_DATABASE"),
#         "USER": config("POSTGRES_USER"),
#         "PASSWORD": config("POSTGRES_PASSWORD"),
#         "HOST": config("POSTGRES_HOST"),
#         "PORT": "5432",
#         "OPTIONS": {
#             "sslmode": "require",
#         },
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        #'OPTIONS': {
        #'min_length': 12,
        # },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
# STATICFILES_DIRS is for directories where Django will search for additional static files
# that aren't tied to any specific app. These files can be served during development.
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# MEDIA_URLS = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ------------Django compressor------------------------------
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # other finders..
    "compressor.finders.CompressorFinder",
)
COMPRESS_ENABLED = True  # compress in Debug=True + Debug =Flase

# Default to False in development unless DEBUG=False
COMPRESS_OFFLINE = True  # Pre-compress files during `collectstatic`

# Specify the backend to handle compression
# COMPRESS_ROOT = STATIC_ROOT
# COMPRESS_URL = STATIC_URL

# # Compress CSS and JS files
# COMPRESS_CSS_FILTERS = [
#     "compressor.filters.css_default.CssAbsoluteFilter",  # Handle relative paths
#     "compressor.filters.cssmin.CSSMinFilter",  # Minify CSS
# ]

# COMPRESS_JS_FILTERS = [
#     "compressor.filters.jsmin.JSMinFilter",  # Minify JS
# ]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "Homepage.CustomUser"
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/login/"
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"

################################Session and Cookie Settings#######################################33
SESSION_COOKIE_AGE = 7200000
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True


# ------------------- django Content security protection------------------------
CSP_BASE_URI = (
    "'self'",
    "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2",
    "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3",
    "https://fonts.googleapis.com",
    "https://fonts.gstatic.com",
    "https://stackpath.bootstrapcdn.com",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome",
    "https://fontawesome.com/",
)
CSP_IMG_SRC = (
    "'self'",  # Allow images from the same domain
    "https://res.cloudinary.com",  # Current allowed sources fpr https
    "http://res.cloudinary.com",  # Current allowed sources for http
    "https://mdbcdn.b-cdn.net",
    "https://dummyimage.com",
    "https://fastly.picsum.photos",
    "https://picsum.photos",  # Allow images from picsum.photos
    "https://placekitten.com",
)

CSP_STYLE_SRC = (
    "'self'",  # Allow styles from the same domain
    "'unsafe-inline'",  # Allow inline styles (if required)
    "https://cdn.jsdelivr.net",  # Allow styles from JSDelivr (for Bootstrap)
    "https://stackpath.bootstrapcdn.com",  # Allow Bootstrap CDN
    "https://fonts.googleapis.com",  # Allow Google Fonts
    "https://maxcdn.bootstrapcdn.com",  # Allow MaxCDN (Bootstrap)
    "https://cdnjs.cloudflare.com",  # Allow FontAwesome from Cloudflare
)


CSP_FONT_SRC = (
    "'self'",
    "https://fonts.googleapis.com",
    "https://fonts.gstatic.com",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome",  # Allow FontAwesome from Cloudflare
    "https://fontawesome.com",
    "https://maxcdn.bootstrapcdn.com",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/webfonts",  # Allow versioned FontAwesome webfonts
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/webfonts",  # Allow any FontAwesome version's webfonts
)


CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",  # Allows inline scripts (consider removing if possible)
    "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2",
    "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js",
    "https://unpkg.com/htmx.org@1.9.10",
    "https://code.jquery.com",  # For jQuery CDN
    "https://cdn.jsdelivr.net/npm/@popperjs",  # For Popper.js CDN
    "https://stackpath.bootstrapcdn.com/bootstrap",  # For Bootstrap
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome",  # FontAwesome
    "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2",
    "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js",
    "https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",  # Add Popper.js
    "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js",  # Add Bootstrap 4.4.1
    "https://unpkg.com/htmx.org@1.9.10",
    "https://code.jquery.com",
    "https://cdn.jsdelivr.net/npm/@popperjs",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome",
    "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js",
    "https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js",
)


###############################Cloudinary Settings For Image Storage###########################

# For cloudinary_storage library only
if DEBUG:
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME"),
        "API_KEY": config("CLOUDINARY_API_KEY"),
        "API_SECRET": config("CLOUDINARY_API_SECRET"),
        # "API_PROXY": "http://proxy.server:3128",
    }
else:
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME"),
        "API_KEY": config("CLOUDINARY_API_KEY"),
        "API_SECRET": config("CLOUDINARY_API_SECRET"),
        "API_PROXY": "http://proxy.server:3128",
    }

# For cloudinary python SDK
import cloudinary

CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET")
if DEBUG:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
    )
else:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        api_proxy="http://proxy.server:3128",
        secure=True,  # Enforces HTTPS
    )
MEDIA_URL = "/media/"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


###########################----------Security Related Settings-----------########################################

# Uncomment these settings only in production
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_SSL_REDIRECT = True

###############################-----------Set Login rate limit For Users-------------#############################
SILENCED_SYSTEM_CHECKS = ["axes.W003"]
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 15  # Number of login attempts allowed before blocking
AXES_LOCK_OUT_AT_FAILURE = False
AXES_COOLOFF_TIME = 0.001
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

###################------------------- Google api-client library settings----------------############
GOOGLE_OAUTH_CLIENT_ID = config("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = config("GOOGLE_OAUTH_CLIENT_SECRET")


if not DEBUG:
    GOOGLE_OAUTH_REDIRECT_URI = (
        "https://osama11111.pythonanywhere.com/accounts/google/login/callback/"
    )
else:
    GOOGLE_OAUTH_REDIRECT_URI = (
        "https://diverse-intense-whippet.ngrok-free.app/accounts/google/login/callback/"
    )


#################-------- csrf settings ----------------######################################
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    "https://diverse-intense-whippet.ngrok-free.app",
    "https://osama11111.pythonanywhere.com",
]


####################---Allauth settings for social account login ----######################
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "CLIENT_ID": config("GOOGLE_OAUTH_CLIENT_ID"),
        "SECRET": config("GOOGLE_OAUTH_CLIENT_SECRET"),
    }
}


################----------CKeditor seetings-------------##############################################
CKEDITOR_CONFIGS = {
    "default": {
        "skin": "moono",
        # 'skin': 'office2013',
        "toolbar_Basic": [["Source", "-", "Bold", "Italic"]],
        "toolbar_YourCustomToolbarConfig": [
            {
                "name": "document",
                "items": [
                    "Source",
                    "-",
                    "Save",
                    "NewPage",
                    "Preview",
                    "Print",
                    "-",
                    "Templates",
                ],
            },
            {
                "name": "clipboard",
                "items": [
                    "Cut",
                    "Copy",
                    "Paste",
                    "PasteText",
                    "PasteFromWord",
                    "-",
                    "Undo",
                    "Redo",
                ],
            },
            {"name": "editing", "items": ["Find", "Replace", "-", "SelectAll"]},
            {
                "name": "forms",
                "items": [
                    "Form",
                    "Checkbox",
                    "Radio",
                    "TextField",
                    "Textarea",
                    "Select",
                    "Button",
                    "ImageButton",
                    "HiddenField",
                ],
            },
            "/",
            {
                "name": "basicstyles",
                "items": [
                    "Bold",
                    "Italic",
                    "Underline",
                    "Strike",
                    "Subscript",
                    "Superscript",
                    "-",
                    "RemoveFormat",
                ],
            },
            {
                "name": "paragraph",
                "items": [
                    "NumberedList",
                    "BulletedList",
                    "-",
                    "Outdent",
                    "Indent",
                    "-",
                    "Blockquote",
                    "CreateDiv",
                    "-",
                    "JustifyLeft",
                    "JustifyCenter",
                    "JustifyRight",
                    "JustifyBlock",
                    "-",
                    "BidiLtr",
                    "BidiRtl",
                    "Language",
                ],
            },
            {"name": "links", "items": ["Link", "Unlink", "Anchor"]},
            {
                "name": "insert",
                "items": [
                    "Image",
                    "Flash",
                    "Table",
                    "HorizontalRule",
                    "Smiley",
                    "SpecialChar",
                    "PageBreak",
                    "Iframe",
                ],
            },
            "/",
            {"name": "styles", "items": ["Styles", "Format", "Font", "FontSize"]},
            {"name": "colors", "items": ["TextColor", "BGColor"]},
            {"name": "tools", "items": ["Maximize", "ShowBlocks"]},
            {"name": "about", "items": ["About"]},
            "/",  # put this to force next toolbar on new line
            {
                "name": "yourcustomtools",
                "items": [
                    # put the name of your editor.ui.addButton here
                    "Preview",
                    "Maximize",
                ],
            },
        ],
        "toolbar": "YourCustomToolbarConfig",  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        # 'height': 291,
        # 'width': '100%',
        # 'filebrowserWindowHeight': 725,
        # 'filebrowserWindowWidth': 940,
        # 'toolbarCanCollapse': True,
        # 'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        "tabSpaces": 4,
        "extraPlugins": ",".join(
            [
                "uploadimage",  # the upload image feature
                # your extra plugins here
                "div",
                "autolink",
                "autoembed",
                "embedsemantic",
                "autogrow",
                # 'devtools',
                "widget",
                "lineutils",
                "clipboard",
                "dialog",
                "dialogui",
                "elementspath",
            ]
        ),
    }
}

# provide error detail for django axes
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "axes": {
            "handlers": ["console"],
            "level": "ERROR",  # Set the level to ERROR to suppress AXES logs
            "propagate": True,
        },
    },
}
