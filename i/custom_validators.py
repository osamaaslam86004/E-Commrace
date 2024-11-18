from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

# Reference Here:
# https://stackoverflow.com/questions/70040740/override-djange-imagefield-extension-validation

image_validator = FileExtensionValidator(
    allowed_extensions=["png", "jpeg", "jpg", "webp"],
    message="Allowed extensions 'png', 'jpeg', 'jpg', 'webp'",
)


class ModifiedImageField(forms.ImageField):
    default_validators = [image_validator]


def file_size_validator(file):
    max_size_mb = 1  # Maximum file size in MB
    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes

    if file.size > max_size:
        raise ValidationError(
            f"File size must be less than {max_size_mb}MB.", params={"value": file}
        )
