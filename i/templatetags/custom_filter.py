from django import template
from urllib.parse import urlparse


register = template.Library()


@register.filter(name="get_value_from_dict")
def get_value_from_dict(dictionary, key):
    return dictionary.get(key, "")


# startswith lookup for string
@register.filter(name="startswith")
def startswith(text, starts):
    # Check if text is a string
    if isinstance(text, str):
        return text.startswith(starts)
    return False


# startswith lookup for URL
@register.filter(name="startswith_for_url")
def startswith(text, starts):
    # Check if text is a string and a valid URL
    if isinstance(text, str):
        # Parse the URL
        parsed_url = urlparse(text)
        # Check if the URL has a scheme (like http, https)
        if parsed_url.scheme in ["http", "https"]:
            return text.startswith(starts)
    return False
