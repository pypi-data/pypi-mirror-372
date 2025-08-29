"""provinces models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    CodeableReference,
    Identifier,
    Reference,
    Signature,
    TimeStampedModel,
)

from .choices import ProvenanceEntryRoleChoices


class ProvenanceAgentWhoReference(BaseReference):
    """provenance agent who reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_who_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.PractitionerReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_who_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRoleReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_who_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "base.OrganizationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_who_reference_organization",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeamReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_who_reference_care_team",
    )
    device = models.ForeignKey(
        "devices.DeviceReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_who_reference_device",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPersonReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_who_reference_related_person",
    )
    group = models.ForeignKey(
        "groups.GroupReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_who_reference_group",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareServiceReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_who_reference_healthcare_service",
    )


class ProvenanceAgentOnBehalfOf(BaseReference):
    """provenance agent on behalf of model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_on_behalf_of_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.PractitionerReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_on_behalf_of_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRoleReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_on_behalf_of_practitioner_role",
    )
    organization = models.ForeignKey(
        "base.OrganizationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_on_behalf_of_organization",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeamReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_on_behalf_of_care_team",
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_on_behalf_of_patient",
    )
    group = models.ForeignKey(
        "groups.GroupReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_on_behalf_of_group",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareServiceReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_on_behalf_of_healthcare_service",
    )


class ProvenanceAgent(TimeStampedModel):
    """provenance agent."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_type",
    )
    role = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_role",
    )
    who = models.ForeignKey(
        ProvenanceAgentWhoReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_who",
    )
    on_behalf_of = models.ForeignKey(
        ProvenanceAgentOnBehalfOf,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_agent_on_behalf_of",
    )


class ProvenanceEntry(TimeStampedModel):
    """provenance entry."""

    role = models.CharField(
        max_length=255,
        null=True,
        choices=ProvenanceEntryRoleChoices.choices,
        default=ProvenanceEntryRoleChoices.REVISION,
    )
    what = models.ForeignKey(
        Reference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_entry_what",
    )
    agent = models.ManyToManyField(
        ProvenanceAgent, related_name="provenance_entry_agent", blank=True
    )


class Provenance(TimeStampedModel):
    """Provinance model."""

    target = models.ManyToManyField(
        Reference, related_name="provinance_target", blank=True
    )
    occurred_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        related_name="provinance_occurred_period",
        null=True,
    )
    occurred_date_time = models.DateTimeField(null=True)
    recorded = models.DateTimeField(null=True)
    policy = ArrayField(models.URLField(), null=True)
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_location",
    )
    authorization = models.ManyToManyField(
        CodeableReference, related_name="provenance_authorization", blank=True
    )
    why = models.TextField(null=True)
    activity = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_activity",
    )
    based_on = models.ManyToManyField(
        Reference, related_name="provenance_based_on", blank=True
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_patient",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="provenance_encounter",
    )
    agent = models.ManyToManyField(
        ProvenanceAgent, related_name="provenance_agent", blank=True
    )
    entity = models.ManyToManyField(
        ProvenanceEntry, related_name="provenance_entity", blank=True
    )
    signature = models.ManyToManyField(
        Signature, related_name="provenance_signature", blank=True
    )


class ProvenanceReference(BaseReference):
    """medication request insurance reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="provinance_reference_identifier",
    )
    provenance = models.ForeignKey(
        Provenance,
        on_delete=models.SET_NULL,
        null=True,
        related_name="provinance_reference_provenance",
    )
