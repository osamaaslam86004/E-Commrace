"""
URL configuration for iii project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from iii.sitemap import sitemaps  # Adjust to your app's location
from iii.views import maintenance

urlpatterns = [
    path("blog/", include(("blog.urls", "blog"))),
    path("", include(("book_.urls", "book_"))),
    path("cart/", include(("cart.urls", "cart"))),
    path("checkout/", include(("checkout.urls", "checkout"))),
    path("", include(("cv_api.urls", "cv_api"))),
    path("", include(("Homepage.urls", "Homepage"))),
    path("", include(("i.urls", "i"))),
    path("admin/", admin.site.urls),
    path("grappelli/", include("grappelli.urls")),  # grappelli URLS
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", include(("django_prometheus.urls", "django_prometheus"))),
    # Maintainance Mode
    path("maintenance/", maintenance, name="maintenance"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
