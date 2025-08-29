"""Location choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class LocationForm(models.TextChoices):
    """Location form choices."""

    BUILDING = "building", _("Building")
    ROOM = "room", _("Room")
    WARD = "ward", _("Ward")
    BED = "bed", _("Bed")
    WING = "wing", _("Wing")
    CORRIDOR = "corridor", _("Corridor")
    VEHICLE = "vehicle", _("Vehicle")
    ROAD = "road", _("Road")
    VIRTUAL = "virtual", _("Virtual")


class LocationStatus(models.TextChoices):
    """Location status choices."""

    ACTIVE = "active", _("Active")
    SUSPENDED = "suspended", _("Suspended")
    INACTIVE = "inactive", _("Inactive")


class LocationMode(models.TextChoices):
    """Location mode choices."""

    INSTANCE = "instance", _("Instance")
    KIND = "kind", _("Kind")


class OperationalStatus(models.TextChoices):
    """Operational status choices."""

    CLOSED = "closed", _("Closed")
    OCCUPIED = "occupied", _("Occupied")
    UNOCCUPIED = "unoccupied", _("Unoccupied")
    ISOLATED = "isolated", _("Isolated")
    HOUSEKEEPING = "housekeeping", _("Housekeeping")
    CONTAMINATED = "contaminated", _("Contaminated")


class LocationCharacteristicChoices(models.TextChoices):
    """Location characteristic choices."""

    WHEEL_CHAIR = "wheel_chair", _("Wheel Chair Accessible")
    HAS_TRANSLATION_SERVICE = (
        "has_translation_service",
        _("Translation services available"),
    )
    HAS_OXY_NITROGEN = "has_oxy_nitrogen", _("Oxygen and Nitrogen available")
    HAS_NEG_PRESSURE = "has_neg_pressure", _("Negative pressure rooms available")
    HAS_ISO_WARD = "has_iso_ward", _("Isolation ward")
    HAS_ICU = "has_icu", _("Intensive Care Unit")
