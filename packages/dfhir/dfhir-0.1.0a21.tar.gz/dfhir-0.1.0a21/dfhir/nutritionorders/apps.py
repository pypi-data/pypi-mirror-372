"""nutrition orders app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NutritionordersConfig(AppConfig):
    """nutrition orders app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.nutritionorders"
    verbose_name = _("Nutrition Orders")
