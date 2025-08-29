"""Group models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Coding,
    ContactDetail,
    Expression,
    Identifier,
    Period,
    Quantity,
    Range,
    Reference,
    RelativeTime,
    TimeStampedModel,
    UsageContext,
)

from . import choices


class GroupCharacteristicDeterminedByReference(BaseReference):
    """Group characteristic determined by reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="group_characteristic_determined_by_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_characteristic_determined_by_reference_device",
    )
    device_metric = models.ForeignKey(
        "devicemetrics.DeviceMetric",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_characteristic_determined_by_reference_device_metric",
    )
    device_definition = models.ForeignKey(
        "devicedefinitions.DeviceDefinition", on_delete=models.CASCADE, null=True
    )


class GroupCharacteristic(TimeStampedModel):
    """Group characteristic model."""

    code = models.ForeignKey(
        CodeableConcept,
        related_name="group_characteristic_code",
        on_delete=models.CASCADE,
        null=True,
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        related_name="group_characteristic_value_code",
        on_delete=models.CASCADE,
        null=True,
    )
    value_boolean = models.BooleanField(null=True)
    value_quantity = models.ForeignKey(
        Quantity,
        related_name="group_characteristic_value_quantity",
        on_delete=models.CASCADE,
        null=True,
    )
    value_range = models.ForeignKey(
        Range,
        related_name="group_characteristic_value_range",
        on_delete=models.CASCADE,
        null=True,
    )
    value_reference = models.ForeignKey(
        Reference,
        related_name="group_characteristic_value_reference",
        on_delete=models.CASCADE,
        null=True,
    )
    value_uri = models.URLField(null=True)
    value_expression = models.ForeignKey(
        Expression,
        related_name="group_characteristic_value_expression",
        on_delete=models.CASCADE,
        null=True,
    )
    exclude = models.BooleanField(null=True)
    description = models.TextField(null=True)
    method = models.ManyToManyField(
        CodeableConcept, related_name="group_characteristic_method", blank=True
    )
    determined_by_reference = models.ForeignKey(
        GroupCharacteristicDeterminedByReference,
        on_delete=models.CASCADE,
        null=True,
        related_name="group_characteristic_determined_by_reference",
    )
    determined_by_expression = models.ForeignKey(
        Expression,
        on_delete=models.CASCADE,
        null=True,
        related_name="group_characteristic_determined_by_expression",
    )
    offset = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="group_characteristic_offset",
    )
    instances_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        null=True,
        related_name="group_characteristic_instances_quantity",
    )
    instances_range = models.ForeignKey(
        Range,
        on_delete=models.CASCADE,
        null=True,
        related_name="group_characteristic_instances_range",
    )
    duration_duration = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        null=True,
        related_name="group_characteristic_duration_duration",
    )
    duration_range = models.ForeignKey(
        Range,
        on_delete=models.CASCADE,
        null=True,
        related_name="group_characteristic_duration_range",
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        null=True,
        related_name="group_characteristic_period",
    )
    timing = models.ManyToManyField(
        RelativeTime, related_name="group_characteristic_timing", blank=True
    )


class GroupMemberEntityReference(BaseReference):
    """Group member entity reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="group_member_entity_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_member_entity_reference_care_team",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_member_entity_reference_device",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_member_entity_reference_group",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthCareService",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_member_entity_reference_healthcare_service",
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_member_entity_reference_location",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_member_entity_reference_organization",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_member_entity_reference_patient",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_member_entity_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_member_entity_reference_practitioner_role",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_member_entity_reference_related_person",
    )
    specimen = models.ForeignKey(
        "specimens.Specimen",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_member_entity_reference_specimen",
    )


class GroupMember(TimeStampedModel):
    """Group member model."""

    entity = models.ForeignKey(
        GroupMemberEntityReference,
        related_name="group_member_entity",
        on_delete=models.CASCADE,
        null=True,
    )
    involvement = models.ManyToManyField(
        CodeableConcept, related_name="group_member_involvement", blank=True
    )
    period = models.ForeignKey(
        Period, related_name="group_member_period", on_delete=models.CASCADE, null=True
    )
    inactive = models.BooleanField(default=False)


class GroupManagingEntityReference(BaseReference):
    """Group managing entity reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="group_managing_entity_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_managing_entity_reference_organization",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_managing_entity_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_managing_entity_reference_practitioner_role",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        null=True,
        related_name="group_managing_entity_reference_related_person",
    )


class Group(TimeStampedModel):
    """Group model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="groups_identifier", blank=True
    )
    uri = models.URLField(null=True)
    version = models.CharField(max_length=255, null=True)
    version_algorithm_string = models.CharField(max_length=255, null=True)
    version_algorithm_coding = models.ForeignKey(
        Coding,
        on_delete=models.CASCADE,
        null=True,
        related_name="group_version_algorithm_coding",
    )
    name = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255, null=True)
    status = models.CharField(
        max_length=255, null=True, choices=choices.GroupStatus.choices
    )
    experimental = models.BooleanField(default=False)
    date = models.DateTimeField(null=True)
    publisher = models.TextField(null=True)
    contact = models.ManyToManyField(
        ContactDetail, related_name="group_contact", blank=True
    )
    description = models.TextField(null=True)
    use_context = models.ManyToManyField(
        UsageContext, related_name="group_use_context", blank=True
    )
    purpose = models.TextField(null=True)
    copyright = models.TextField(null=True)
    copyright_label = models.CharField(max_length=255, null=True)
    type = models.CharField(
        max_length=255, null=True, choices=choices.GroupTypeChoices.choices
    )
    membership = models.CharField(
        max_length=255, null=True, choices=choices.GroupMembershipChoices.choices
    )
    code = models.ForeignKey(
        CodeableConcept, related_name="group_code", on_delete=models.CASCADE, null=True
    )
    quantity = models.IntegerField(null=True)
    managing_entity = models.ForeignKey(
        GroupManagingEntityReference,
        related_name="group_managing_entity",
        on_delete=models.CASCADE,
        null=True,
    )
    combination_method = models.CharField(
        max_length=255, null=True, choices=choices.GroupCombinationMethodChoices.choices
    )
    combination_threshold = models.IntegerField(null=True)
    characteristic = models.ManyToManyField(
        GroupCharacteristic, related_name="group_characteristic", blank=True
    )
    member = models.ManyToManyField(
        GroupMember, related_name="group_member", blank=True
    )


class GroupReference(BaseReference):
    """Group reference."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="group_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    group = models.ForeignKey(
        Group, related_name="group_reference_group", on_delete=models.CASCADE, null=True
    )
