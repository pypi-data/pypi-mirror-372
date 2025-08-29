"""observation definition model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class QualifiedValueGenderChoices(TextChoices):
    """qualified value gender choices."""

    MALE = "male", _("Male")
    FEMALE = "female", _("Female")
    OTHER = "other", _("Other")
    UNKNOWN = "unknown", _("Unknown")


class QualifiedValueRangeCategoryChoices(TextChoices):
    """qualified value range category choices."""

    REFERENCE = "reference", _("Reference")
    CRITICAL = "critical", _("Critical")
    ABSOLUTE = "absolute", _("Absolute")


class ObservationDefinitionStatusChoices(TextChoices):
    """observation definition status choices."""

    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    RETIRED = "retired", _("Retired")
    UNKNOWN = "unknown", _("Unknown")


class ObservationDefinitionPermittedDataTypeChoices(TextChoices):
    """observation definition permitted data type choices."""

    QUANTITY = "Quantity", _("Quantity")
    CODEABLE_CONCEPT = "codeableconcept", _("Codeable Concept")
    STRING = "string", _("String")
    BOOLEAN = "boolean", _("Boolean")
    INTEGER = "integer", _("Integer")
    RANGE = "range", _("Range")
    RATIO = "ratio", _("Ratio")
    SAMPLED_DATA = "sampled_data", _("Sampled Data")
    TIME = "time", _("Time")
    DATE = "date", _("Date")
    DATETIME = "datetime", _("Datetime")
    PERIOD = "period", _("Period")
