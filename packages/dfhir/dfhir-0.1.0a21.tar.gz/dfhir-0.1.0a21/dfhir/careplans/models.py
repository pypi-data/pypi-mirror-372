"""care plan models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)

from . import choices


class CarePlanBasedOnReference(BaseReference):
    """care plan based on reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_based_on_identifier",
    )
    care_plan = models.ForeignKey(
        "CarePlan",
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_based_on_care_plan",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_based_on_service_request",
    )
    # TODO: request_orientation = models.ForeignKey("RequestOrientation", on_delete=models.SET_NULL, null=True)
    # TODO: nutrition_order = models.ForeignKey("NutritionOrder", on_delete=models.SET_NULL, null=True)


class CarePlanCustodianReference(BaseReference):
    """custodian contributor reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="custodian_contributor_reference_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.SET_NULL, null=True
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner", on_delete=models.SET_NULL, null=True
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole", on_delete=models.SET_NULL, null=True
    )
    device = models.ForeignKey("devices.Device", on_delete=models.SET_NULL, null=True)
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson", on_delete=models.SET_NULL, null=True
    )
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.SET_NULL, null=True
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam", on_delete=models.SET_NULL, null=True
    )


class CarePlanContributorReference(CarePlanCustodianReference):
    """contributor reference."""

    pass


class CarePlanAddressReference(BaseReference):
    """care plan address reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_address_reference_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition", on_delete=models.SET_NULL, null=True
    )
    medication_administration = models.ForeignKey(
        "medicationadministrations.MedicationAdministration",
        on_delete=models.SET_NULL,
        null=True,
    )


class CarePlanAddressesCodeableReference(TimeStampedModel):
    """care plan addresses codeable reference."""

    reference = models.ForeignKey(
        CarePlanAddressReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_addresses_codeable_reference",
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_addresses_concept",
    )


class CarePlanPlannedActivityReference(BaseReference):
    """care plan planned activity reference."""

    identifier = models.ForeignKey(Identifier, on_delete=models.SET_NULL, null=True)
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_planned_activity_reference_appointment",
    )
    # TODO: communication_request = models.ForeignKey("communication.CommunicationRequest", on_delete=models.SET_NULL, null=True)
    # TODO: device_request = models.ForeignKey("devicerequests.DeviceRequest", on_delete=models.SET_NULL, null=True)
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_planned_activity_reference_medication_request",
    )
    # TODO: nutrition_order = models.ForeignKey(
    #     "nutritionorders.NutritionOrder",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     related_name="care_plan_planned_activity_reference_nutrition_order",
    # )
    # TODO: task = models.ForeignKey("tasks.Task", on_delete=models.SET_NULL, null=True)
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_planned_activity_reference_service_request",
    )
    # TODO: vision_prescription = models.ForeignKey("visionprescriptions.VisionPrescription", on_delete=models.SET_NULL, null=True)
    # request_orchestration = models.ForeignKey("requestorchestrations.RequestOrchestration", on_delete=models.SET_NULL, null=True)
    # TODO: immunization_recommendation = models.ForeignKey("immunizationrecommendations.ImmunizationRecommendation", on_delete=models.SET_NULL, null=True)
    # TODO: supply_request = models.ForeignKey("supplyrequests.SupplyRequest", on_delete=models.SET_NULL, null=True)


class CarePlanActivity(TimeStampedModel):
    """care plan activity."""

    performer_activity = models.ManyToManyField(
        "base.CodeableReference",
        blank=True,
        related_name="care_plan_activity_performer_activity",
    )
    progress = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="care_plan_activity_progress"
    )
    planned_activity_reference = models.ForeignKey(
        CarePlanPlannedActivityReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_activity_planned_activity_reference",
    )


class CarePlan(TimeStampedModel):
    """care plan."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="care_plan_identifier"
    )
    based_on = models.ManyToManyField(
        CarePlanBasedOnReference, blank=True, related_name="care_plan_based_on"
    )
    replaces = models.ManyToManyField(
        "CarePlanReference", blank=True, related_name="care_plan_replaces"
    )
    part_of = models.ManyToManyField(
        "CarePlanReference", blank=True, related_name="care_plan_part_of"
    )
    status = models.CharField(
        max_length=255, null=True, choices=choices.CareplanStatusChoices.choices
    )
    intent = models.CharField(
        max_length=255, null=True, choices=choices.CarePlanIntentChoices.choices
    )
    category = models.ManyToManyField(
        "base.CodeableConcept", blank=True, related_name="care_plan_category"
    )
    title = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_subject",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_encounter",
    )
    period = models.ForeignKey(
        "base.Period",
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_period",
    )
    created = models.DateTimeField(null=True)
    custodian = models.ForeignKey(
        CarePlanCustodianReference,
        null=True,
        related_name="care_plan_custodian",
        on_delete=models.CASCADE,
    )
    contributor = models.ManyToManyField(
        CarePlanContributorReference, blank=True, related_name="care_plan_contributor"
    )
    care_team = models.ManyToManyField(
        "careteams.CareTeamReference", blank=True, related_name="care_plan_care_team"
    )
    addresses = models.ManyToManyField(
        CarePlanAddressesCodeableReference,
        blank=True,
        related_name="care_plan_addresses",
    )
    supporting_info = models.ManyToManyField(
        "base.Reference", blank=True, related_name="care_plan_supporting_info"
    )
    # TODO: goal = models.ManyToManyField(
    #     "base.Reference", blank=True, related_name="care_plan_goal"
    # )
    activity = models.ManyToManyField(
        CarePlanActivity, blank=True, related_name="care_plan_activity"
    )
    note = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="care_plan_note"
    )


class CarePlanReference(BaseReference):
    """care plan reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_reference_identifier",
    )
    care_plan = models.ForeignKey(
        CarePlan,
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_reference_care_plan",
    )


class CarePlanDeviceRequestReference(BaseReference):
    """care plan device request reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_device_request_reference_identifier",
    )
    care_plan = models.ForeignKey(
        CarePlan,
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_plan_device_request_reference_care_plan",
    )
    # device_request = models.ForeignKey(
    #     "devicerequests.DeviceRequest",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     related_name="care_plan_device_request_reference_device_request",
    # )
