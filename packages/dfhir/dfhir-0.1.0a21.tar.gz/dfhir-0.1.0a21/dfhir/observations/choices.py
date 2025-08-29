"""choices module for dfhir observations."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class ObservationStatus(TextChoices):
    """observation status choices."""

    REGISTERED = "registered", _("Registered")
    PRELIMINARY = "preliminary", _("Preliminary")
    FINAL = "final", _("Final")
    AMENDED = "amended", _("Amended")
    CORRECTED = "corrected", _("Corrected")
    CANCELLED = "cancelled", _("Cancelled")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")


class AbsentReason(TextChoices):
    """absent reason choices."""

    UNKNOWN = "unknown", _("Unknown")
    ASKED_BUT_UNKNOWN = "asked-unknown", _("Asked but unknown")
    TEMPORARILY_UNKNOWN = "temporarily_unknown", _("Temporarily unknown")
    NOT_ASKED = "not_asked", _("Not asked")
    ASKED_BUT_DECLINED = "asked_declined", _("Asked but declined")
    MASKED = "masked", _("Masked")
    NOT_APPLICABLE = "not_applicable", _("Not applicable")
    UNSUPPORTED = "unsupported", _("Unsupported")
    AS_TEXT = "as_text", _("As text")
    ERROR = "error", _("Error")
    NOT_A_NUMBER = "not_a_number", _("Not a number")
    NEGATIVE_INFINITY = "negative_infinity", _("Negative infinity")
    POSITIVE_INFINITY = "positive_infinity", _("Positive infinity")
    NOT_PERFORMED = "not_performed", _("Not performed")
    NOT_PERMITTED = "not_permitted", _("Not permitted")


class ReferenceNormalValues(TextChoices):
    """reference normal values choices."""

    NEGATIVE = "negative", _("Negative")
    ABSENT = "absent", _("Absent")


class ReferenceType(TextChoices):
    """reference type choices."""

    TYPE = "type", _("Type")
    NORMAL_RANGE = "normal_range", _("Normal Range")
    RECOMMENDED_RANGE = "recommended_range", _("Recommended Range")
    TREATMENT_RANGE = "treatment_range", _("Treatment Range")
    THERAPEUTIC_DESIRED_LEVEL = (
        "therapeutic_desired_level",
        _("Therapeutic Desired Level"),
    )
    PRE_THERAPEUTIC_DESIRED_LEVEL = (
        "pre_therapeutic_desired_level",
        _("Pre-Therapeutic Desired Level"),
    )
    POST_THERAPEUTIC_DESIRED_LEVEL = (
        "post_therapeutic_desired_level",
        _("Post-Therapeutic Desired Level"),
    )
    ENDOCRINE = "endocrine", _("Endocrine")
    PRE_PUBERTY = "pre_puberty", _("Pre-Puberty")
    FOLLICULAR_STAGE = "follicular_stage", _("Follicular Stage")
    MID_CYCLE = "mid_cycle", _("Mid-Cycle")
    LUTEAL = "luteal", _("Luteal")
    POST_MENOPAUSE = "post_menopause", _("Post-Menopause")


class TriggeredByType(TextChoices):
    """triggered by type choices."""

    REFLEX = "reflex", _("Reflex")
    REPEAT = "repeat", _("Repeat")
    RE_RUN = "re_run", _("Re-run")
