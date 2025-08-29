"""Choices for the base app."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class TelecomUseChoices(models.TextChoices):
    """Telecom use choices."""

    HOME = "home", _("home")
    WORK = "work", _("work")
    TEMP = "temp", _("temp")
    OLD = "old", _("old")
    MOBILE = "mobile", _("mobile")


class AddressUseChoices(models.TextChoices):
    """Address use choices."""

    HOME = "home", _("home")
    WORK = "work", _("work")
    TEMP = "temp", _("temp")
    OLD = "old", _("old")
    BILLING = "billing", _("billing")


class AddressTypeChoices(models.TextChoices):
    """Address type choices."""

    POSTAL = "postal", _("postal")
    PHYSICAL = "physical", _("physical")
    BOTH = "both", _("both")


class GenderChoices(models.TextChoices):
    """Gender choices."""

    MALE = "male", _("male")
    FEMALE = "female", _("female")
    OTHER = "other", _("other")
    UNKNOWN = "unknown", _("unknown")


class ParticipantType(models.TextChoices):
    """Participant types."""

    ADM = "ADM", _("Admitter")
    ATTD = "ATND", _("Attender")
    CALLBCK = "CALLBCK", _("Callback Contact")  # # codespell:ignore
    CON = "CON", _("Consultant")
    DIS = "DIS", _("Discharger")
    EMERGENCY = "emergency", _("Emergency")
    ESCORT = "ESC", _("escort")
    REF = "REF", _("Referrer")
    TRANSLATOR = "translator", _("Translator")


class ParticipantStatus(models.TextChoices):
    """Participant Status."""

    ACCEPTED = "accepted", _("Accepted")
    DECLINED = "declined", _("Declined")
    TENTATIVE = "tentative", _("Tentative")
    NEEDS_ACTION = "needs_action", _("Needs Action")


class TelecomSystemChoices(models.TextChoices):
    """Telecom system choices."""

    PHONE = "phone", _("phone")
    FAX = "fax", _("fax")
    EMAIL = "email", _("email")
    SMS = "sms", _("sms")
    URL = "url", _("url")
    OTHER = "other", _("other")


class ContactPointUseChoices(models.TextChoices):
    """Contact point use choices."""

    HOME = "home", _("home")
    WORK = "work", _("work")
    TEMP = "temp", _("temp")
    OLD = "old", _("old")
    MOBILE = "mobile", _("mobile")


class ContactPointSystemChoices(models.TextChoices):
    """Contact point system choices."""

    PHONE = "phone", _("phone")
    FAX = "fax", _("fax")
    EMAIL = "email", _("email")
    SMS = "sms", _("sms")
    URL = "url", _("url")
    OTHER = "other", _("other")


class HumanNameUseChoices(models.TextChoices):
    """Human name use choices."""

    USUAL = "usual", _("usual")
    OFFICIAL = "official", _("official")
    TEMP = "temp", _("temp")
    NICKNAME = "nickname", _("nickname")
    ANONYMOUS = "anonymous", _("anonymous")
    OLD = "old", _("old")
    MAIDEN = "maiden", _("maiden")


class DaysOfWeekChoices(models.TextChoices):
    """Days of week choices."""

    MON = "mon", _("Monday")
    TUE = "tue", _("Tuesday")
    WED = "wed", _("Wednesday")
    THU = "thu", _("Thursday")
    FRI = "fri", _("Friday")
    SAT = "sat", _("Saturday")
    SUN = "sun", _("Sunday")


class QuantityComparatorChoices(models.TextChoices):
    """Quantity comparator choices."""

    EQUAL = "eq", _("Equal")
    NOT_EQUAL = "ne", _("Not Equal")
    GREATER_THAN = "gt", _("Greater Than")
    LESS_THAN = "lt", _("Less Than")
    GREATER_OR_EQUAL = "ge", _("Greater or Equal")
    LESS_OR_EQUAL = "le", _("Less or Equal")


class ParticipationStatusChoices(models.TextChoices):
    """Participation statuses."""

    ACCEPTED = "accepted", _("Accepted")
    DECLINED = "declined", _("Declined")
    TENTATIVE = "tentative", _("Tentative")
    NEEDSACTION = "needs-action", _("Needs Action")


class RepeatDurationUnits(models.TextChoices):
    """Repeat duration units."""

    SECOND = "s", _("second")
    MINUTE = "min", _("minute")
    HOUR = "h", _("hour")
    DAY = "d", _("day")
    WEEK = "wk", _("week")
    MONTH = "mo", _("month")
    YEAR = "yr", _("year")


class RelatedArtifactTypeChoices(models.TextChoices):
    """Related artifact type choices."""

    DOCUMENTATION = "documentation", _("documentation")
    JUSTIFICATION = "justification", _("justification")
    CITATION = "citation", _("citation")
    PREDECESSOR = "predecessor", _("predecessor")
    SUCCESSOR = "successor", _("successor")
    DERIVED_FROM = "derived-from", _("derived-from")
    DEPENDS_ON = "depends-on", _("depends-on")
    COMPOSED_OF = "composed-of", _("composed-of")
    PART_OF = "part-of", _("part-of")
    REPLACES = "replaces", _("replaces")
    AMENDS = "amends", _("amends")
    APPENDS = "appends", _("appends")
    TRANSFORMS = "transforms", _("transforms")
    AMENDED_WITH = "amended-with", _("amended-with")
    APPENDED_WITH = "appended-with", _("appended-with")
    CITES = "cites", _("cites")
    CITED_BY = "cited-by", _("cited-by")
    COMMENTS_ON = "comments-on", _("comments-on")
    COMMENTS_IN = "comments-in", _("comments-in")
    CONTAINS = "contains", _("contains")
    CONTAINED_IN = "contained-in", _("contained-in")
    CORRECTS = "corrects", _("corrects")
    CORRECTION_IN = "correction-in", _("correction-in")
    REPLACED_WITH = "replaced-with", _("replaced-with")
    RETRACTS = "retracts", _("retracts")
    RETRACTED_BY = "retracted-by", _("retracted-by")
    SIGNS = "signs", _("signs")
    SIMILAR_TO = "similar-to", _("similar-to")
    SUPPORTS = "supports", _("supports")
    SUPPORTED_WITH = "supported-with", _("supported-with")
    TRANSFORMED_INT0 = "transformed-into", _("transformed-into")
    TRANSFORMED_WITH = "transformed-with", _("transformed-with")
    DOCUMENTS = "documents", _("documents")
    SPECIFICATION_OF = "specification-of", _("specification-of")
    CREATED_WITH = "created-with", _("created-with")
    CITE_AS = "cite-as", _("cite-as")


class PublicationStatusChoices(models.TextChoices):
    """Publication status choices."""

    DRAFT = "draft", _("draft")
    ACTIVE = "active", _("active")
    RETIRED = "retired", _("retired")
    UNKNOWN = "unknown", _("unknown")


class MonetaryComponentChoices(models.TextChoices):
    """Monetary component choices."""

    BASE = "base", _("base")
    SURCHARGE = "surcharge", _("surcharge")
    DISCOUNT = "discount", _("discount")
    TAX = "tax", _("tax")
    INFORMATIONAL = "informational", _("informational")


class TriggerDefinitionTypeChoices(models.TextChoices):
    """Trigger definition type choices."""

    NAMED_EVENT = "named-event", _("Named Event")
    PERIODIC = "periodic", _("Periodic")
    DATA_CHANGED = "data-changed", _("Data Changed")
    DATA_ADDED = "data-added", _("Data Added")
    DATA_MODIFIED = "data-modified", _("Data Modified")
    DATA_REMOVED = "data-removed", _("Data Removed")
    DATA_ACCESSED = "data-accessed", _("Data Accessed")
    DATA_ACCESSED_ENDED = "data-accessed-ended", _("Data Accessed Ended")
