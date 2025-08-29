"""nutrition intake app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NutritionintakesConfig(AppConfig):
    """nutrition intake app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.nutritionintakes"
    verbose_name = _("Nutrition Intakes")
