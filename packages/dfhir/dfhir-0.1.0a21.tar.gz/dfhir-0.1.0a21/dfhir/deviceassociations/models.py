"""Deviceassociations models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Period,
    TimeStampedModel,
)


class DeviceAssociationOperationOperatorReference(BaseReference):
    """DeviceAssociationOperationOperatorReference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="device_association_operation_operator_reference_identifier",
    )

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.SET_NULL,
        null=True,
        related_name="device_association_operation_operator_reference_patient",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        related_name="device_association_operation_operator_reference_practitioner",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.SET_NULL,
        null=True,
        related_name="device_association_operation_operator_reference_related_person",
    )


class DeviceAssociationOperation(TimeStampedModel):
    """DeviceAssociationOperation model."""

    status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_association_operation_status",
    )
    operator = models.ManyToManyField(
        DeviceAssociationOperationOperatorReference,
        related_name="device_association_operation_operator",
        blank=True,
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_association_operation_period",
    )


class DeviceAssociationSubjectReference(BaseReference):
    """DeviceAssociationSubjectReference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_association_subject_reference_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_association_subject_reference_patient",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_association_subject_reference_group",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_association_subject_reference_practitioner",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_association_subject_reference_related_person",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_association_subject_reference_device",
    )


class DeviceAssociation(TimeStampedModel):
    """DeviceAssociation model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="device_association_identifier",
        blank=True,
    )
    device = models.ForeignKey(
        "devices.DeviceReference",
        on_delete=models.CASCADE,
        related_name="device_association_device",
    )
    relationship = models.ManyToManyField(
        CodeableConcept,
        related_name="device_association_relationship",
        blank=True,
    )
    status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="device_association_status",
        null=True,
    )
    status_reason = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="device_association_status_reason",
    )
    subject = models.ForeignKey(
        DeviceAssociationSubjectReference,
        on_delete=models.CASCADE,
        related_name="device_association_subject",
    )
    body_structure = models.ForeignKey(
        "bodystructures.BodyStructureReference",
        on_delete=models.CASCADE,
        null=True,
        related_name="device_association_body_structure",
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_association_period",
    )
    operation = models.ManyToManyField(
        DeviceAssociationOperation,
        related_name="device_association_operation",
        blank=True,
    )
