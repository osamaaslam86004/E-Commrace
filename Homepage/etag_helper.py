import hashlib
import json
from decimal import Decimal

from i.browsing_history import your_browsing_history


def decimal_converter(obj):
    """Converts Decimal to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    raise TypeError(f"Type {type(obj)} not serializable")


def generate_etag_HomepageView(request):
    """Generates ETag based on browsing history stored in cookies."""
    browsing_history = your_browsing_history(request)  # Fetch browsing history

    # Serialize browsing history safely
    data = json.dumps(
        {"history": browsing_history}, sort_keys=True, default=decimal_converter
    ).encode()

    return f'"{hashlib.md5(data).hexdigest()}"'  # Return quoted ETag
