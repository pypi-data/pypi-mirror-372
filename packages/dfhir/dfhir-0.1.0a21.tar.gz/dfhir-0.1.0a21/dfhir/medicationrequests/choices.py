"""medication requests model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class DoseAndRateType(TextChoices):
    """dose type model."""

    CALCULATED = "calculated", _("Calculated")
    ORDERED = "ordered", _("Ordered")


class MedicationRequestStatusReasons(TextChoices):
    """medication request status reason choices."""

    TRY_ANOTHER_TREATMENT_FIRST = (
        "try_another_treatment_first",
        _("Try another treatment first"),
    )
    PRESCRIPTION_REQUIRES_CLARIFICATION = (
        "prescription_requires_clarification",
        _("Prescription requires clarification"),
    )
    DRUG_LEVEL_TOO_HIGH = "drug_level_too_high", _("Drug level too high")
    ADMISSION_TO_HOSPITAL = "admission_to_hospital", _("Admission to hospital")
    LAB_INTERFERENCE_ISSUES = "lab_interference_issues", _("Lab interference issues")
    PATIENT_NOT_AVAILABLE = "patient_not_available", _("Patient not available")
    PATIENT_IS_PREGNANT = "patient_is_pregnant", _("Patient is pregnant")
    PATIENT_IS_BREASTFEEDING = "patient_is_breastfeeding", _("Patient is breastfeeding")
    ALLERGY = "allergy", _("Allergy")
    DRUG_INTERACTS_WITH_ANOTHER_DRUG = (
        "drug_interacts_with_another_drug",
        _("Drug interacts with another drug"),
    )
    DUPLICATE_THERAPY = "duplicate_therapy", _("Duplicate therapy")
    SUSPECTED_INTOLERANCE = "suspected_intolerance", _("suspected intolerance")
    PATIENT_SCHEDULED_FOR_SURGERY = (
        "patient_scheduled_for_surgery",
        _("Patient scheduled for surgery"),
    )
    WAITING_FOR_OLD_DRUG_TO_WASH_OUT = (
        "waiting_for_old_drug_to_wash_out",
        _("Waiting for old drug to wash out"),
    )


class MedicationRequestPriority(TextChoices):
    """medication requests priority."""

    ROUTINE = "routine", _("Routine")
    URGENT = "urgent", _("Urgent")
    ASAP = "asap", _("ASAP")
    STAT = "stat", _("STAT")


class MedicationRequestPerformerType(TextChoices):
    """medication request performer type."""

    REGISTERED_NURSE = "registered_nurse", _("Registered nurse")
    ONCOLOGY_NURSE = "oncology_nurse", _("Oncology nurse")
    PAIN_CONTROL_NURSE = "pain_control_nurse", _("Pain control nurse")
    PHYSICIAN = "physician", _("Physician")
    PHARMACIST = "pharmacist", _("Pharmacist")


class CourseOfTherapyType(TextChoices):
    """course of therapy type."""

    CONTINUOUS_LONG_TERM_THERAPY = (
        "continuous_long_term_therapy",
        _("Continuous long term therapy"),
    )
    SHORT_COURSE_THERAPY = "short_course_therapy", _("Short course therapy")
    SEASONAL = "seasonal", _("Seasonal")


class MedicationRequestStatus(TextChoices):
    """medication request status."""

    ACTIVE = "active", _("Active")
    ON_HOLD = "on_hold", _("On hold")
    ENDED = "ended", _("Ended")
    STOPPED = "stopped", _("Stopped")
    COMPLETED = "completed", _("Completed")
    CANCELLED = "cancelled", _("Cancelled")
    ENTERED_IN_ERROR = "entered_in_error", _("Entered in error")
    DRAFT = "draft", _("Draft")
    UNKNOWN = "unknown", _("Unknown")


class MedicationIntent(TextChoices):
    """medication request intent."""

    PLAN = "plan", _("Plan")
    ORDER = "order", _("Order")
    ORIGINAL_ORDER = "original_order", _("Original order")
    FILLER_ORDER = "filler_order", _("Filler order")
    INSTANCE_ORDER = "instance_order", _("Instance order")
    OPTION = "option", _("Option")


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
