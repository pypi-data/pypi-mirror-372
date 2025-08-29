"""medication model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class MedicationStatus(TextChoices):
    """medication status choices."""

    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    ENTERED_IN_ERROR = "entered_in_error", _("Entered in error")


class MedicationIngredientStrength(TextChoices):
    """medication ingredient strength choices."""

    SUFFICIENT = "sufficient", _("Sufficient")
    SMALL_AMOUNT = "small_amount", _("Small amount")


class DoseAdministrationAid(TextChoices):
    """dose administration aid."""

    BLISTER_PACK = "blister_pack", _("Blister pack")
    DOSETTE = "dosette", _("Dosette")
    SACHETS = "sachets", _("Sachets")


class SubstitutionReason(TextChoices):
    """substitution reason."""

    CONTINUING_THERAPY = "continuing_therapy", _("Continuing therapy")
    FORMULARY_POLICY = "formulary_policy", _("Formulary policy")
    OUT_OF_STOCK = "out of stock", _("Out of stock")
    REGULATORY_REQUIREMENTS = "regulatory_requirements", _("Regulatory requirements")
