"""Encounter model choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class EncounterStatus(models.TextChoices):
    """Choices for the status of an encounter."""

    PLANNED = "planned", _("Planned")
    IN_PROGRESS = "in-progress", _("In Progress")
    ON_HOLD = "on-hold", _("On Hold")
    DISCHARGED = "discharged", _("Discharged")
    COMPLETED = "completed", _("Completed")
    CANCELLED = "cancelled", _("Cancelled")
    DISCONTINUED = "discontinued", _("Discontinued")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")


class SubjectStatus(models.TextChoices):
    """Choices for the status of a subject."""

    ARRIVED = "arrived", _("Arrived")
    TRIAGED = "triaged", _("Triaged")
    RECEIVING_CARE = "receiving_care", _("Receiving Care")
    DEPARTED = "departed", _("Departed")
    ON_LEAVE = "on_leave", _("On Leave")


class AdmissionChoices(models.TextChoices):
    """Choices for admission types."""

    TRANSFERRED = "transferred", _("Transferred")
    OUTPATIENT_DEPARTMENT = "outpatient-department", _("Outpatient Department")
    EMERGENCY_DEPARTMENT = "emergency-department", _("Emergency or Accident Department")
    GP_REFERRAL = "gp-referral", _("General Practitioner Referral")
    MP_REFERRAL = "mp-referral", _("Medical Practitioner Referral")
    REHABILITATION = "rehabilitation", _("Rehabilitation Department")
    PSYCHIATRY = "psychiatry", _("Psychiatric Department")
    BORN_IN_HOSPITAL = "born-in-hospital", _("Born in Hospital")
    NURSING_HOME = "nursing-home", _("From Nursing Home")
    OTHER = "other", _("Other")


class DischargeChoices(models.TextChoices):
    """Choices for discharge destinations."""

    HOME = "home", _("Home")
    OTHER_HEALTH_CARE_FACILITY = (
        "other_health_care_facility",
        _("Other Health Care Facility"),
    )
    HOSPICE = "hospice", _("Hospice")
    LONG_TERM_CARE = "long-term-care", _("Long Term Care")
    LEFT_AGAINST_ADVICE = "left-against-advice", _("Left Against Advice")
    EXPIRED = "expired", _("Expired")
    PSYCHIATRIC_HOSPITAL = "psychiatric-hospital", _("Psychiatric Hospital")
    REHABILITATION = "rehabilitation", _("Rehabilitation")
    SKILLED_NURSING = "skilled-nursing", _("Skilled Nursing")
    ALTERNATIVE_HOME = "alternative-home", _("Alternative Home")
    OTHER = "other", _("Other")


class EncounterClassChoices(models.TextChoices):
    """Choices for the class of an encounter."""

    INPATIENT_ENCOUNTER = "inpatient-encounter", _("Inpatient Encounter")
    AMBULATORY = "outpatient-encounter", _("Outpatient Encounter")
    OBSERVATION_ENCOUNTER = "observation-encounter", _("Observation Encounter")
    EMERGENCY = "emergency", _("Emergency")
    VIRTUAL = "virtual", _("Virtual")
    HOME_HEALTH = "home-health", _("Home Health")


class EncounterPriority(models.TextChoices):
    """Choices for the priority of an encounter."""

    ASAP = "asap", _("ASAP")
    CALLBACK_RESULTS = "callback-results", _("Callback Results")
    ELECTIVE = "elective", _("Elective")
    EMERGENCY = "emergency", _("Emergency")
    PREOP = "preop", _("Preop")
    AS_NEEDED = "as-needed", _("As Needed")
    ROUTINE = "routine", _("Routine")
    RUSH_REPORTING = "rush-reporting", _("Rush Reporting")
    STAT = "stat", _("Stat")
    TIMING_CRITICAL = "timing-critical", _("Timing Critical")
    USE_AS_DIRECTED = "use-as-directed", _("Use As Directed")
    URGENT = "urgent", _("Urgent")
    CALLBACK_FOR_SCHEDULING = "callback-for-scheduling", _("Callback for Scheduling")
    CALLBACK_PLACER_FOR_SCHEDULING = (
        "callback-placer-for-scheduling",
        _("Callback Placer for Scheduling"),
    )
    CONTACT_PATIENT_FOR_SCHEDULING = (
        "contact-patient-for-scheduling",
        _("Contact Patient for Scheduling"),
    )


class EncounterLocationStatusChoices(models.TextChoices):
    """Choices for the status of an encounter location."""

    PLANNED = "planned", _("Planned")
    ACTIVE = "active", _("Active")
    RESERVED = "reserved", _("Reserved")
    COMPLETED = "completed", _("Completed")
