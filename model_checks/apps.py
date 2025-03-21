from django.apps import AppConfig


class ModelChecksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "model_checks"

    def ready(self):
        from model_checks.check_choices_lentgh import run_model_field_choices_checks
        from model_checks.nulls_blanks import run_model_field_checks
        from model_checks.verbose_name_check import run_verbose_name_check

        # Register your checks, e.g., connect to django's startup signal
