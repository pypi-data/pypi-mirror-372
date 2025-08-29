"""image selection app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ImagingselectionsConfig(AppConfig):
    """Image selections config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.imagingselections"
    verbose_name = _("Image Selections")
