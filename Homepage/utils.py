from datetime import timedelta

from axes.models import AccessAttempt
from django.conf import settings
from django.utils.timezone import now


def time_in_minutes(
    access_log_time,
):
    # Calculate remaining lockout time
    lockout_time = access_log_time + timedelta(hours=settings.AXES_COOLOFF_TIME)
    print(f"lockout time: {lockout_time}")

    # Convert timedelta to minutes before using max()
    remaining_time = max((lockout_time - now()).total_seconds() / 60, 0)
    print(f"Remaining time: {remaining_time} minutes")

    return remaining_time


def format_remaining_time(delta_seconds):
    """Formats the remaining time into a readable format."""
    if delta_seconds <= 0:
        return "0 seconds"

    delta = timedelta(seconds=delta_seconds)
    days, remainder = divmod(delta.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    time_parts = []

    if days:
        time_parts.append(f"{int(days)} Days")
    if hours:
        time_parts.append(f"{int(hours)} Hours")
    if minutes:
        time_parts.append(f"{int(minutes)} Minutes")
    if seconds:
        time_parts.append(f"{int(seconds)} seconds")

    return " ".join(time_parts)


class AccessLogTime:

    @staticmethod
    def access_log_time_by_username(username):
        access_log_time = (
            AccessAttempt.objects.filter(username=username)
            .order_by("-attempt_time")
            .values_list("attempt_time", flat=True)
            .first()
        )
        return access_log_time

    @staticmethod
    def access_log_time_by_ip(ip):
        access_log_time = (
            AccessAttempt.objects.filter(ip_address=ip)
            .order_by("-attempt_time")
            .values_list("attempt_time", flat=True)
            .first()
        )
        return access_log_time

    @staticmethod
    def access_log_time_by_user_agent(user_agent):
        access_log_time = (
            AccessAttempt.objects.filter(user_agent__icontains=user_agent)
            .order_by("-attempt_time")
            .values_list("attempt_time", flat=True)
            .first()
        )
        return access_log_time
