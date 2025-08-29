"""Healthcare Services models."""

from django.db import models

from dfhir.base.models import (
    Attachment,
    Availability,
    BaseReference,
    CodeableConcept,
    ExtendedContactDetail,
    Identifier,
    OrganizationReference,
    Period,
    Quantity,
    Range,
    Reference,
    TimeStampedModel,
)


class HealthCareServiceReference(BaseReference):
    """Healthcare Service Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="healthcareservice_reference_identifier",
    )
    healthcare_service = models.ForeignKey(
        "HealthcareService",
        on_delete=models.DO_NOTHING,
        related_name="healthcareservice_reference",
        null=True,
    )


class HealthCareServiceCodeableReference(TimeStampedModel):
    """CodeableReference model."""

    reference = models.ForeignKey(
        HealthCareServiceReference,
        on_delete=models.DO_NOTHING,
        related_name="codeable_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="healthcareservice_codeableconcept",
        null=True,
    )


class ClinicalSpecialty(TimeStampedModel):
    """Clinical Specialty model."""

    code = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255)


class ServiceCategory(TimeStampedModel):
    """Service Category model."""

    code = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255, null=True)


class HealthCareServiceEligibilityValue(TimeStampedModel):
    """Healthcare Service Eligibility Value model."""

    value_codeable_concept = models.ForeignKey(
        CodeableConcept, on_delete=models.DO_NOTHING, null=True
    )
    value_boolean = models.BooleanField(null=True)
    value_quantity = models.ForeignKey(Quantity, on_delete=models.DO_NOTHING, null=True)
    value_range = models.ForeignKey(Range, on_delete=models.DO_NOTHING, null=True)
    value_reference = models.ForeignKey(
        Reference, on_delete=models.DO_NOTHING, null=True
    )


class HealthcareServiceEligibility(TimeStampedModel):
    """Healthcare Service Eligibility model."""

    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="healthcareserviceeligibility_code",
    )
    value = models.ForeignKey(
        HealthCareServiceEligibilityValue, on_delete=models.DO_NOTHING, null=True
    )
    comment = models.TextField(null=True)
    period = models.ForeignKey(Period, on_delete=models.DO_NOTHING, null=True)


class HealthcareService(TimeStampedModel):
    """Healthcare Service model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="healthcareservice_identifier", blank=True
    )
    active = models.BooleanField(default=True)
    offered_in = models.ManyToManyField(
        HealthCareServiceReference,
        related_name="healthcareservice_offered_in",
        blank=True,
    )
    name = models.CharField(max_length=255)
    location = models.ManyToManyField(
        "locations.LocationReference",
        related_name="healthcare_service_location",
        blank=True,
    )
    provided_by = models.ForeignKey(
        OrganizationReference, on_delete=models.DO_NOTHING, null=True
    )
    comment = models.TextField(null=True)
    extra_details = models.TextField(null=True)
    photo = models.ForeignKey(Attachment, on_delete=models.CASCADE, null=True)
    coverage_area = models.ManyToManyField(
        "locations.LocationReference",
        related_name="healthcareservice_coverage_area",
        blank=True,
    )
    referral_required = models.BooleanField(default=False)
    referral_method = models.ManyToManyField(
        CodeableConcept, related_name="healthcareservice_referral_method", blank=True
    )
    appointment_required = models.BooleanField(default=False)
    type = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="healthcareservice_type"
    )
    specialty = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="healthcareservice_specialty"
    )
    category = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="healthcareservice_category"
    )
    service_provision_code = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="healthcareservice_service_provision_code",
    )
    program = models.ManyToManyField(
        CodeableConcept, related_name="healthcareservice_program", blank=True
    )
    characteristic = models.ManyToManyField(
        CodeableConcept, related_name="healthcareservice_characteristics", blank=True
    )
    communication = models.ManyToManyField(
        CodeableConcept, related_name="healthcareservice_communication", blank=True
    )
    contact = models.ManyToManyField(
        ExtendedContactDetail, related_name="healthcareservice_contact", blank=True
    )
    availability = models.ForeignKey(
        Availability,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="healthcareservice_availability",
    )
    endpoint = models.ManyToManyField(
        "endpoints.Endpoint", related_name="healthcareservice_endpoint", blank=True
    )
    eligibility = models.ManyToManyField(
        HealthcareServiceEligibility,
        related_name="healthcareservice_eligibility",
        blank=True,
    )
