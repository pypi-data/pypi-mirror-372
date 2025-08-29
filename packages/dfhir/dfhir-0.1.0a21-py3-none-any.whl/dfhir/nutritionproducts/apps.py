"""Nutrition Products app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NutritionproductsConfig(AppConfig):
    """Nutrition Products app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.nutritionproducts"
    verbose_name = _("Nutrition Products")
