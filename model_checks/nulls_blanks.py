from typing import Field, Iterable, Optional

from django.apps import apps
from django.core.checks import Tags, register
from django.core.exceptions import ValidationError as Error
from django.db import models


def get_project_model_fields() -> Iterable[Field]:
    for app in apps.app_configs:
        app_config = apps.get_app_config(app)
        # Skip third party apps.
        if app_config.path.find("site-packages") > -1:
            continue
        app_models = app_config.get_models()
        for model in app_models:
            for field in model._meta.get_fields():
                yield field


@register(Tags.models)
def run_model_field_checks(*args, **kwargs) -> Iterable[Error]:
    errors = []
    for field in get_project_model_fields():
        error = check_blank_null(field)
        if error is not None:
            errors.append(error)
    return errors


def check_blank_null(field: models.Field) -> Optional[Error]:
    is_primary_key = getattr(field, "primary_key", False)
    is_text_or_char_field = isinstance(field, models.CharField) or isinstance(
        field, models.TextField
    )

    if (
        is_text_or_char_field
        and not is_primary_key
        and field.null is True
        and field.blank is True
    ):
        ft = field.get_internal_type()
        msg = f"{ft} cannot have null=True blank=True."
        hint = f"Set null=False on field '{field.name}'."
        return Error(msg, hint, field, id="H001")

    if (
        not is_text_or_char_field
        and not is_primary_key
        and field.null is False
        and field.blank is True
    ):
        ft = field.get_internal_type()
        msg = f"{ft} cannot have null=False blank=True."
        hint = f"Set null=True or blank=False on field '{field.name}'."
        return Error(msg, hint, field, id="H002")
