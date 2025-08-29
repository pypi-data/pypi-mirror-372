"""Care Teams models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    ContactPoint,
    Identifier,
    OrganizationReference,
    Period,
    TimeStampedModel,
)
from dfhir.patients.models import PatientGroupReference

from . import choices


class CareTeamParticipantOnBehalfOfReference(BaseReference):
    """Care Team Participant On Behalf Of Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="care_team_participant_on_behalf_of_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner", on_delete=models.CASCADE, null=True
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole", on_delete=models.CASCADE, null=True
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson", on_delete=models.CASCADE, null=True
    )
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, null=True)
    organization = models.ForeignKey(
        OrganizationReference,
        related_name="care_team_participant_on_behalf_of_reference_organization",
        on_delete=models.CASCADE,
        null=True,
    )
    care_team = models.ForeignKey("CareTeam", on_delete=models.CASCADE, null=True)


class CareTeamParticipantMemberReference(CareTeamParticipantOnBehalfOfReference):
    """Care Team Participant Member Reference model."""


class CareTeamParticipant(TimeStampedModel):
    """Care Team Participant model."""

    role = models.ForeignKey(
        CodeableConcept,
        related_name="care_team_participants_role",
        on_delete=models.CASCADE,
        null=True,
    )
    member = models.ForeignKey(
        CareTeamParticipantMemberReference,
        related_name="care_team_participants_member",
        on_delete=models.CASCADE,
        null=True,
    )
    on_behalf_of = models.ForeignKey(
        CareTeamParticipantOnBehalfOfReference,
        related_name="care_team_participants_on_behalf_of",
        on_delete=models.CASCADE,
        null=True,
    )
    effective_period = models.ForeignKey(
        Period,
        related_name="care_team_participants_effective_period",
        on_delete=models.CASCADE,
        null=True,
    )
    effective_timing = models.ForeignKey(
        "base.Timing",
        related_name="care_team_participants_effective_timing",
        on_delete=models.CASCADE,
        null=True,
    )


class CareTeam(TimeStampedModel):
    """Care Team model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="care_teams_identifier", blank=True
    )
    status = models.CharField(
        max_length=255, choices=choices.CareTeamStatusChoices.choices, null=True
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="care_teams_category", blank=True
    )
    name = models.CharField(max_length=255, null=True)
    subject = models.ForeignKey(
        PatientGroupReference,
        related_name="care_teams_subject",
        on_delete=models.CASCADE,
        null=True,
    )
    period = models.ForeignKey(
        Period, related_name="care_teams_period", on_delete=models.CASCADE, null=True
    )
    participant = models.ManyToManyField(
        CareTeamParticipant, related_name="care_teams_participant", blank=True
    )
    reason = models.ManyToManyField(
        "conditions.ConditionCodeableReference",
        related_name="care_teams_reason_code",
        blank=True,
    )
    managing_organization = models.ManyToManyField(
        OrganizationReference,
        related_name="care_teams_managing_organization",
        blank=True,
    )
    telecom = models.ManyToManyField(
        ContactPoint, related_name="care_teams_telecom", blank=True
    )
    note = models.ManyToManyField(
        Annotation, related_name="care_teams_note", blank=True
    )


class CareTeamReference(BaseReference):
    """Care Team reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="care_team_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    care_team = models.ForeignKey(
        CareTeam,
        related_name="care_team_reference_care_team",
        on_delete=models.CASCADE,
        null=True,
    )
