"""task models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    CodeableReference,
    Identifier,
    TimeStampedModel,
)
from dfhir.coverages.models import CoverageClaimResponseReference
from dfhir.provenances.models import ProvenanceReference
from dfhir.tasks.choices import (
    TaskIntentChoices,
    TaskPriorityChoices,
    TaskStatusChoices,
)


class TaskReference(BaseReference):
    """task reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_reference_identifier",
    )
    task = models.ForeignKey(
        "Task",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_reference_task",
    )


class TaskRequesterReference(BaseReference):
    """task requester reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requester_reference_identifier",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requester_reference_device",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requester_reference_organization",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requester_reference_patient",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_requester_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_requester_reference_practitioner_role",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_requester_reference_related_person",
    )


class TaskRequestedPerformerReference(BaseReference):
    """task requested performer reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requested_performer_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_requested_performer_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_requested_performer_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requested_performer_reference_organization",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        related_name="task_requested_practitioner_care_team",
        null=True,
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requested_practitioner_healthcare_service",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requested_performer_reference_patient",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requested_performer_reference_device",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_requested_performer_reference_related_person",
    )


class TaskRequestedPerformerCodeableReference(TimeStampedModel):
    """task requested performer codeable reference."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requested_performer_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        TaskRequestedPerformerReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requested_performer_codeable_reference_reference",
    )


class TaskOwnerReference(BaseReference):
    """task owner reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_owner_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_owner_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_owner_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_owner_reference_organization",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        related_name="task_owner_practitioner_care_team",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_owner_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_owner_reference_related_person",
    )


class TaskPerformerActorReference(BaseReference):
    """task performer actor reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="task_performer_actor_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_performer_actor_reference_practitioner",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_performer_actor_reference_device",
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_performer_actor_reference_organization",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_performer_actor_reference_practitioner_role",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        related_name="task_performer_actor_reference_practitioner_care_team",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_performer_actor_reference_patient",
    )

    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_performer_actor_reference_related_person",
    )


class TaskRestrictionRecipientReference(BaseReference):
    """task restriction recipient reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="task_restriction_recipient_reference",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_restriction_recipient_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_restriction_recipient_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_restriction_recipient_reference_organization",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        related_name="task_requested_practitioner_care_team",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_restriction_recipient_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_restriction_recipient_reference_related_person",
    )


class TaskPerformer(TimeStampedModel):
    """task performer model."""

    function = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_performer_model",
    )
    actor = models.ForeignKey(
        TaskPerformerActorReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_performer_actor",
    )


class TaskRestriction(TimeStampedModel):
    """task restriction model."""

    repetition = models.PositiveIntegerField(null=True)
    period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_restriction_period",
    )
    recipient = models.ManyToManyField(
        TaskRestrictionRecipientReference,
        blank=True,
        related_name="ask_restrictions_recipient",
    )


class TaskInput(TimeStampedModel):
    """task input model."""

    type = models.ForeignKey(
        CodeableConcept,
        null=False,
        on_delete=models.DO_NOTHING,
        related_name="task_input_type",
    )
    value = models.CharField(null=True, max_length=255)


class TaskOutput(TimeStampedModel):
    """task output model."""

    type = models.ForeignKey(
        CodeableConcept,
        null=False,
        on_delete=models.DO_NOTHING,
        related_name="task_output_type",
    )
    value = models.CharField(null=True, max_length=255)


class Task(TimeStampedModel):
    """task model."""

    identifier = models.ManyToManyField(
        Identifier, blank=False, related_name="task_identifier"
    )
    # TODO: instantiate_canonical = models.ForeignKey(
    #     "ActivityDefinitionCAnonical",
    #     related_name="task_instantiate_canonical",
    #     null=True,
    #     on_delete=models.DO_NOTHING,
    # )
    instantiate_uri = models.URLField(null=True)
    based_on = models.ManyToManyField(
        "base.Reference", blank=True, related_name="task_based_on"
    )
    group_identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="task_group_identifier",
        null=True,
    )
    part_of = models.ManyToManyField(
        TaskReference, blank=True, related_name="task_part_of"
    )
    status = models.CharField(
        max_length=255, null=True, choices=TaskStatusChoices.choices
    )
    status_reason = models.ForeignKey(
        CodeableReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_status_reason",
    )
    business_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_business_status",
    )
    intent = models.CharField(
        max_length=255, null=True, choices=TaskIntentChoices.choices
    )
    priority = models.CharField(
        max_length=255, null=True, choices=TaskPriorityChoices.choices
    )
    do_not_perform = models.BooleanField(default=False)
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="task_code",
        null=True,
    )
    description = models.TextField(null=True)
    focus = models.ForeignKey(
        "base.Reference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_focus",
    )
    for_value = models.ForeignKey(
        "base.Reference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_for",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_encounter",
    )
    requested_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requested_period",
    )
    execution_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_execution_period",
    )
    authored_on = models.DateTimeField(null=True)
    last_modified = models.DateTimeField(null=True)
    requester = models.ForeignKey(
        TaskRequesterReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_requester",
    )
    requested_performer = models.ManyToManyField(
        TaskRequestedPerformerCodeableReference,
        blank=True,
        related_name="task_requested_performer",
    )
    owner = models.ForeignKey(
        TaskOwnerReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_owner",
    )
    performer = models.ManyToManyField(
        TaskPerformer, related_name="task_performer", blank=True
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="task_location",
    )
    reason = models.ManyToManyField(
        CodeableReference, blank=True, related_name="task_reason"
    )
    insurance = models.ManyToManyField(
        CoverageClaimResponseReference, blank=True, related_name="task_insurance"
    )
    note = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="task_note"
    )
    relevant_history = models.ManyToManyField(
        ProvenanceReference, blank=True, related_name="task_relevant_history"
    )
    restriction = models.ForeignKey(
        TaskRestriction,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="task_restriction",
    )
    input = models.ManyToManyField(TaskInput, blank=True, related_name="task_input")
    output = models.ManyToManyField(TaskOutput, blank=True, related_name="task_output")
