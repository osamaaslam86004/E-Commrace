from typing import Iterable, Optional

from django.apps import apps
from django.core.checks import Error, Tags, register
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
def run_verbose_name_check(*args, **kwargs) -> Iterable[Error]:
    """Check that every model field has a 'verbose_name' attribute set."""
    errors = []

    for field in get_project_model_fields():
        error = check_field_verbose_name(field)
        if error is not None:
            errors.append(error)

    return errors


def check_field_verbose_name(field: models.Field) -> Optional[Error]:
    """Verify that the 'verbose_name' attribute is set for the given field."""
    verbose_name = getattr(field, "verbose_name", None)

    # Some fields like AutoField may not require verbose_name
    ignored_fields = (models.AutoField, models.ForeignKey, models.OneToOneField)

    if isinstance(field, ignored_fields):
        return None

    if not verbose_name or verbose_name == field.name.replace("_", " "):
        return Error(
            f"Field '{field.name}' in model '{field.model.__name__}' is missing a proper verbose_name.",
            hint="Set a descriptive verbose_name to improve readability in Django Admin and forms.",
            obj=field,
            id="H004",
        )

    return None
