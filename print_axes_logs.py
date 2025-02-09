import os

import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iii")
django.setup()

from axes.models import AccessAttempt, AccessLog


def print_axes_logs():
    # Print fields from axes_accesslog
    print("AccessLog Fields:")
    access_logs = AccessLog.objects.all()
    for log in access_logs:
        print(log.__dict__)  # Print all fields

    # Print fields from axes_accessattempt
    print("\nAccessAttempt Fields:")
    access_attempts = AccessAttempt.objects.all()
    for attempt in access_attempts:
        print(attempt.__dict__)  # Print all fields


if __name__ == "__main__":
    print_axes_logs()
