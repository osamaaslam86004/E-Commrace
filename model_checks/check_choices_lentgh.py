from typing import Iterable, Optional

from django.apps import apps
from django.core.checks import Tags, register
from django.core.exceptions import ValidationError as Error
from django.db import models


def get_project_model_fields() -> Iterable[models.Field]:
    """Retrieve all fields from project models, skipping third-party apps."""
    for app_config in apps.get_app_configs():
        # Skip third-party apps
        if "site-packages" in app_config.path:
            continue
        for model in app_config.get_models():
            for field in model._meta.get_fields():
                yield field


@register(Tags.models)
def run_model_field_choices_checks(*args, **kwargs) -> Iterable[Error]:
    """Run validation checks on model fields."""
    errors = []
    for field in get_project_model_fields():
        error = check_field_validations(field)
        if error is not None:
            errors.append(error)
    return errors


def check_field_validations(field: models.Field) -> Optional[Error]:
    """
    Performs the following checks:
    1. If a CharField has choices, ensure each choice does not exceed max_length.
    2. If choices are present, ensure max_length is defined.
    3. Ensure choices are not used in a TextField.
    """
    if isinstance(field, models.CharField) and field.choices:
        max_length = getattr(field, "max_length", None)

        if max_length is None:
            return Error(
                f"Field '{field.name}' has choices but is missing 'max_length'.",
                hint="Specify max_length for CharField with choices.",
                obj=field,
                id="H003",
            )

        for choice in field.choices:
            choice_value = str(choice[0])  # Ensure it's a string
            if len(choice_value) > max_length:
                return Error(
                    f"Choice '{choice_value}' for field '{field.name}' exceeds max_length={max_length}.",
                    hint="Reduce the length of the choice value.",
                    obj=field,
                    id="H003",
                )

    elif isinstance(field, models.TextField) and field.choices:
        return Error(
            f"Field '{field.name}' uses TextField with choices.",
            hint="Use CharField instead of TextField for choices.",
            obj=field,
            id="H004",
        )

    return None
