
import time
from django.core.cache import cache
from django.http import HttpResponseForbidden


class GlobalRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the client's IP address
        ip = self.get_client_ip(request)
        print(f"remote address-----------{request.META.get("REMOTE_ADDR")}")
        print(f"ip-----------{ip}")

        # Define rate limit parameters
        rate_limit = 8  # requests per hour
        cache_key = f"rate_limit_{ip}"

        # Get the current request count and timestamp from the cache
        request_count, first_request_time = cache.get(cache_key, (0, time.time()))

        # Check if the time window has expired (1 hour)
        current_time = time.time()
        if current_time - first_request_time > 3600:  # 3600 seconds = 1 hour
            request_count = 0  # Reset count after an hour
            first_request_time = current_time

        # Increment the request count
        request_count += 1

        # Store the updated count and timestamp back in the cache
        cache.set(cache_key, (request_count, first_request_time), timeout=3600)

        # Check if the limit is exceeded
        if request_count > rate_limit:
            return HttpResponseForbidden("Too many requests")

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Retrieve the client's IP address from the request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[
                0
            ]  # Return the first IP in case of multiple proxies
        return request.META.get("REMOTE_ADDR")
