"""activity definition choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ActivityDefinitionStatus(models.TextChoices):
    """Activity definition status."""

    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    RETIRED = "retired", _("Retired")
    UNKNOWN = "unknown", _("Unknown")


class ActivityDefinitionKindChoices(models.TextChoices):
    """Activity definition kind choices."""

    APPOINTMENT = "appointment", _("Appointment")
    CARE_PLAN = "care-plan", _("Care Plan")
    CLAIM = "claim", _("Claim")
    COMMUNICATION_REQUEST = "communication-request", _("CommunicationRequest")
    COVERAGE_ELIGIBILITY_REQUEST = (
        "coverage-eligibility-request",
        _("CoverageEligibilityRequest"),
    )
    DEVICE_REQUEST = "device-request", _("DeviceRequest")
    ENROLLMENT_REQUEST = "enrollment-request", _("EnrollmentRequest")
    IMMUNIZATION_RECOMMENDATION = (
        "immunization-recommendation",
        _("ImmunizationRecommendation"),
    )
    MEDICATION_REQUEST = "medication-request", _("Medication Request")
    NUTRITION_ORDER = "nutrition-order", _("Nutrition Order")
    REQUEST_ORCHESTRATION = "request-orchestration", _("Request Orchestration")
    SERVICE_REQUEST = "service-request", _("Service Request")
    SUPPLY_REQUEST = "supply-request", _("Supply Request")
    TASK = "task", _("Task")
    TRANSPORT = "transport", _("Transport")
    VISION_PRESCRIPTION = "vision-prescription", _("Vision Prescription")


class ActivityDefinitionIntentChoices(models.TextChoices):
    """Activity definition intent choices."""

    PROPOSAL = "proposal", _("Proposal")
    PLAN = "plan", _("Plan")
    DIRECTIVE = "directive", _("Directive")
    ORDER = "order", _("Order")
    ORIGINAL_ORDER = "original-order", _("Original Order")
    REFLEX_ORDER = "reflex-order", _("Reflex Order")
    FILTER_ORDER = "filter-order", _("Filter Order")
    INSTANCE_ORDER = "instance-order", _("Instance Order")
    OPTION = "option", _("Option")


class ActivityDefinitionPriorityChoices(models.TextChoices):
    """Activity definition priority choices."""

    ROUTINE = "routine", _("Routine")
    URGENCY = "urgency", _("Urgency")
    ASAP = "asap", _("ASAP")
    STAT = "stat", _("STAT")


class ActivityDefinitionParticipantTypeChoices(models.TextChoices):
    """activity definition participant type choices."""

    CARETEAM = "careteam", _("Care Team")
    DEVICE = "device", _("Device")
    GROUP = "group", _("Group")
    HEALTHCARE_SERVICE = "healthcareservice", _("Healthcare Service")
    LOCATION = "location", _("Location")
    ORGANIZATION = "organization", _("Organization")
    PATIENT = "patient", _("Patient")
    PRACTITIONER = "practitioner", _("Practitioner")
    PRACTITIONER_ROLE = "practitionerrole", _("Practitioner Role")
    RELATED_PERSON = "relatedperson", _("Related Person")
