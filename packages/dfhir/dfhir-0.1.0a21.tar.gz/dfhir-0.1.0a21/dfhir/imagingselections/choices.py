"""imaging selections model choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ImagingSelectionInstanceImageRegion2DRegionTypeChoices(models.TextChoices):
    """Imaging Selection Instance Image Region Type Choices."""

    POINT = "point", _("Point")
    POLYLINE = "polyline", _("Polyline")
    MULTIPOINT = "multipoint", _("Multipoint")
    CIRCLE = "circle", _("Circle")
    ELLIPSE = "ellipse", _("Ellipse")


class ImagingSelectionInstanceImageRegion3DRegionTypeChoices(models.TextChoices):
    """Imaging Selection Instance Image Region Type Choices."""

    POINT = "point", _("Point")
    MULTIPOINT = "multipoint", _("Multipoint")
    POLYLINE = "polyline", _("Polyline")
    POLYGON = "polygon", _("Polygon")
    ELLIPSE = "ellipse", _("Ellipse")
    ELLIPSOID = "ellipsoid", _("Ellipsoid")


class ImagingSelectionStatusChoices(models.TextChoices):
    """Imaging Selection Status Choices."""

    AVAILABLE = "available", _("Available")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    INACTIVE = "inactive", _("Inactive")
    UNKNOWN = "unknown", _("Unknown")
