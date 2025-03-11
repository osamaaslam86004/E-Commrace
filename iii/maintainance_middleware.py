from django.conf import settings
from django.shortcuts import render


class MaintenanceModeMiddleware:
    """Middleware to display a maintenance page when the site is under maintenance."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Check if maintenance mode is enabled in settings
        if getattr(settings, "MAINTENANCE_MODE", False):
            # Allow staff or superusers to bypass maintenance mode

            """
            Use this validation inly if This Middleware is
            after AuthenticationMiddleware in settings.py
            """
            # if request.user.is_authenticated and (
            #     request.user.is_staff or request.user.is_superuser
            # ):
            #     return self.get_response(request)

            # Render a maintenance page
            return render(request, "503.html", status=503)

        return self.get_response(request)
