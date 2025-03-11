import re

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class MaintenanceModeMiddleware:
    """Middleware to display a maintenance page when the site is under maintenance."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        # Allow staff or superusers to bypass maintenance mode

        # Use this validation only if This Middleware is
        # placed after AuthenticationMiddleware in settings.py
        """
        if getattr(request, "user", None):
            if request.user.is_authenticated and (
                request.user.is_staff or request.user.is_superuser
            ):
                return self.get_response(request)

        # Check if maintenance mode is enabled in settings
        path = request.META.get("PATH_INFO", "")

        if getattr(settings, "MAINTENANCE_MODE", False) and path != reverse(
            "maintenance"
        ):
            response = redirect(reverse("maintenance"), permanent=True)
            return response

        return self.get_response(request)
