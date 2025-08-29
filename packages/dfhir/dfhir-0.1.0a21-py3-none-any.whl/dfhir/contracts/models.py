"""Contract models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    Annotation,
    Attachment,
    BaseReference,
    CodeableConcept,
    Coding,
    Identifier,
    Money,
    OrganizationReference,
    Period,
    Quantity,
    Reference,
    Signature,
    SimpleQuantity,
    TimeStampedModel,
    Timing,
)

from . import choices


class ContractAuthorReference(BaseReference):
    """Contract Author Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_author_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="contract_author_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="contract_author_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="contract_author_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="contract_author_reference_organization",
        null=True,
    )


class ContractSubjectReference(BaseReference):
    """Subject reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="subject_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="subject_reference_patient",
        null=True,
    )


class ContractContentDefinitionPublisherReference(BaseReference):
    """Contract Content Definition Publisher Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_content_definition_publisher_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="contract_content_definition_publisher_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="contract_content_definition_publisher_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="contract_content_definition_publisher_reference_organization",
        null=True,
    )


class ContractContentDefinition(TimeStampedModel):
    """Contract Content Definition model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_content_definition_type",
        null=True,
    )
    sub_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_content_definition_sub_type",
        null=True,
    )
    publisher = models.ForeignKey(
        ContractContentDefinitionPublisherReference,
        on_delete=models.CASCADE,
        related_name="contract_content_definition_publisher",
        null=True,
    )
    publication_date = models.DateTimeField(null=True)
    publication_status = models.CharField(
        max_length=255,
        null=True,
        choices=choices.ContractContentDefinitionPublicationStatusChoices.choices,
    )
    copyright = models.TextField(null=True)


class ContractTermSecurityLabel(TimeStampedModel):
    """Contract Term Security Label model."""

    number = ArrayField(models.IntegerField(), null=True)
    classification = models.ForeignKey(
        Coding,
        on_delete=models.CASCADE,
        related_name="contract_term_security_label_classification",
        null=True,
    )
    category = models.ManyToManyField(
        Coding, related_name="contract_term_security_label_category", blank=True
    )
    control = models.ManyToManyField(
        Coding, related_name="contract_term_security_label_control", blank=True
    )


class ContractTermOfferPartyReferenceReference(BaseReference):
    """Contract Term Offer Party Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_term_offer_party_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="contract_term_offer_party_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="contract_term_offer_party_reference_related_person",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="contract_term_offer_party_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="contract_term_offer_party_reference_practitioner_role",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="contract_term_offer_party_reference_device",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="contract_term_offer_party_reference_group",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="contract_term_offer_party_reference_organization",
        null=True,
    )


class ContractTermOfferParty(TimeStampedModel):
    """Contract Term Offer Party model."""

    reference = models.ManyToManyField(
        ContractTermOfferPartyReferenceReference,
        related_name="contract_term_offer_party_reference",
        blank=True,
    )
    role = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_offer_party_role",
        null=True,
    )


class ContractTermOfferAnswer(TimeStampedModel):
    """Contract Term Offer Answer model."""

    value_boolean = models.BooleanField(null=True)
    value_decimal = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    value_integer = models.IntegerField(null=True)
    value_date = models.DateField(null=True)
    value_date_time = models.DateTimeField(null=True)
    value_time = models.TimeField(null=True)
    value_string = models.CharField(max_length=255, null=True)
    value_uri = models.URLField(null=True)
    value_attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="contract_term_offer_answer_attachment",
        null=True,
    )
    value_coding = models.ForeignKey(
        Coding,
        on_delete=models.CASCADE,
        related_name="contract_term_offer_answer_coding",
        null=True,
    )
    value_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        related_name="contract_term_offer_answer_quantity",
        null=True,
    )
    value_reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name="contract_term_offer_answer_reference",
        null=True,
    )


class ContractTermOffer(TimeStampedModel):
    """Contract Term Offer model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="contract_term_offer_identifier",
        blank=True,
    )
    party = models.ManyToManyField(
        ContractTermOfferParty,
        related_name="contract_term_offer_party",
        blank=True,
    )
    topic = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name="contract_term_offer_topic",
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_offer_type",
        null=True,
    )
    decision = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_offer_decision",
        null=True,
    )
    decision_mode = models.ManyToManyField(
        CodeableConcept,
        related_name="contract_term_offer_decision_mode",
        blank=True,
    )
    answer = models.ManyToManyField(
        ContractTermOfferAnswer,
        related_name="contract_term_offer_answer",
        blank=True,
    )
    text = models.TextField(null=True)
    link_id = ArrayField(models.CharField(max_length=255), null=True)
    security_label_number = ArrayField(models.IntegerField(), null=True)


class ContractTermAssetContext(TimeStampedModel):
    """Contract Term Asset Context model."""

    reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_context_reference",
        null=True,
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_context_code",
        null=True,
    )
    text = models.TextField(null=True)


class ContractTermAssetValuedItemResponsibleReference(BaseReference):
    """Contract Term ASet Valued item responsible model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="contract_tem_asset_valued_item_responsible_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="contract_tem_asset_valued_item_responsible_organization",
        on_delete=models.CASCADE,
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        related_name="contract_tem_asset_valued_item_responsible_patient",
        on_delete=models.CASCADE,
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        related_name="contract_tem_asset_valued_item_responsible_practitioner",
        on_delete=models.CASCADE,
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        related_name="contract_tem_asset_valued_item_responsible_practitioner_role",
        on_delete=models.CASCADE,
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        related_name="contract_tem_asset_valued_item_responsible_related_person",
        on_delete=models.CASCADE,
        null=True,
    )


class ContractTermAssetValuedItemRecipientReference(BaseReference):
    """Contract Term Asset Valued Item Recipient model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="contract_tem_asset_valued_item_recipient_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="contract_tem_asset_valued_item_recipient_organization",
        on_delete=models.CASCADE,
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        related_name="contract_tem_asset_valued_item_recipient_patient",
        on_delete=models.CASCADE,
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        related_name="contract_tem_asset_valued_item_recipient_practitioner",
        on_delete=models.CASCADE,
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        related_name="contract_tem_asset_valued_item_recipient_practitioner_role",
        on_delete=models.CASCADE,
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        related_name="contract_tem_asset_valued_item_recipient_related_person",
        on_delete=models.CASCADE,
        null=True,
    )


class ContractTermAssetValuedItem(TimeStampedModel):
    """Contract Term Asset Valued Item model."""

    entity_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_valued_item_entity_codeable_concept",
        null=True,
    )
    entity_reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_valued_item_entity_reference",
        null=True,
    )
    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_valued_item_identifier",
        null=True,
    )
    effective_time = models.DateTimeField(null=True)
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_valued_item_quantity",
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_valued_item_unit_price",
        null=True,
    )
    factor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    points = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_valued_item_net",
        null=True,
    )
    payment = models.CharField(max_length=255, null=True)
    payment_date = models.DateTimeField(null=True)
    responsible = models.ForeignKey(
        ContractTermAssetValuedItemResponsibleReference,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_valued_item_responsible",
        null=True,
    )
    recipient = models.ForeignKey(
        ContractTermAssetValuedItemRecipientReference,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_valued_item_recipient",
        null=True,
    )
    link_id = ArrayField(models.CharField(max_length=255), null=True)
    security_label_number = ArrayField(models.IntegerField(), null=True)


class ContractTermAsset(TimeStampedModel):
    """Contract Term Asset model."""

    scope = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_scope",
        null=True,
    )
    type = models.ManyToManyField(
        CodeableConcept,
        related_name="contract_term_asset_type",
        blank=True,
    )
    type_reference = models.ManyToManyField(
        Reference,
        related_name="contract_term_asset_type_reference",
        blank=True,
    )
    subtype = models.ManyToManyField(
        CodeableConcept,
        related_name="contract_term_asset_subtype",
        blank=True,
    )
    relationship = models.ForeignKey(
        Coding,
        on_delete=models.CASCADE,
        related_name="contract_term_asset_relationship",
        null=True,
    )

    context = models.ManyToManyField(
        ContractTermAssetContext,
        related_name="contract_term_asset_context",
        blank=True,
    )
    condition = models.TextField(null=True)
    period_type = models.ManyToManyField(
        CodeableConcept,
        related_name="contract_term_asset_period_type",
        blank=True,
    )
    period = models.ManyToManyField(
        Period,
        related_name="contract_term_asset_period",
        blank=True,
    )
    use_period = models.ManyToManyField(
        Period,
        related_name="contract_term_asset_use_period",
        blank=True,
    )
    text = models.TextField(null=True)
    link_id = ArrayField(models.CharField(max_length=255), null=True)
    answer = models.ManyToManyField(
        ContractTermOfferAnswer,
        related_name="contract_term_asset_answer",
        blank=True,
    )
    security_label_number = ArrayField(models.IntegerField(), null=True)
    valued_item = models.ManyToManyField(
        ContractTermAssetValuedItem,
        related_name="contract_term_asset_valued_item",
        blank=True,
    )


class ContractTermActionSubjectReferenceReference(BaseReference):
    """Contract Term Action Subject Reference Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_term_action_subject_reference_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="contract_term_action_subject_reference_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="contract_term_action_subject_reference_reference_related_person",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="contract_term_action_subject_reference_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="contract_term_action_subject_reference_reference_practitioner_role",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="contract_term_action_subject_reference_reference_device",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="contract_term_action_subject_reference_reference_group",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="contract_term_action_subject_reference_reference_organization",
        null=True,
    )


class ContractTermActionSubject(TimeStampedModel):
    """Contract Term Action Subject model."""

    reference = models.ManyToManyField(
        ContractTermActionSubjectReferenceReference,
        related_name="contract_term_action_subject_reference",
        blank=True,
    )
    role = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_action_subject_role",
        null=True,
    )


class ContractTermActionRequesterReference(BaseReference):
    """Contract Term Action Requester Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_term_action_requester_reference_identifier",
        null=True,
    )

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="contract_term_action_requester_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="contract_term_action_requester_reference_related_person",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="contract_term_action_requester_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="contract_term_action_requester_reference_practitioner_role",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="contract_term_action_requester_reference_device",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="contract_term_action_requester_reference_group",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="contract_term_action_requester_reference_organization",
        null=True,
    )


class ContractTermActionPerformerReference(BaseReference):
    """Contract Term Action Performer Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer_reference_identifier",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer_reference_related_person",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer_reference_practitioner_role",
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer_reference_care_team",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer_reference_device",
        null=True,
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer_reference_substance",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer_reference_organization",
        null=True,
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer_reference_location",
        null=True,
    )


class ContractTermActionReasonReference(BaseReference):
    """Contract Term Action Reason Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_term_action_reason_reference_identifier",
        null=True,
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.CASCADE,
        related_name="contract_term_action_reason_reference_condition",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.CASCADE,
        related_name="contract_term_action_reason_reference_observation",
        null=True,
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.CASCADE,
        related_name="contract_term_action_reason_reference_diagnostic_report",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.CASCADE,
        related_name="contract_term_action_reason_reference_document_reference",
        null=True,
    )
    # questionnaire = models.ForeignKey(
    #     "questionnaires.Questionnaire",
    #     on_delete=models.CASCADE,
    #     related_name="contract_term_action_reason_reference_questionnaire",
    #     null=True,
    # )
    # questionnaire_response = models.ForeignKey(
    #     "questionnaireresponses.QuestionnaireResponse",
    #     on_delete=models.CASCADE,
    #     related_name="contract_term_action_reason_reference_questionnaire_response",
    #     null=True,
    # )


class ContractTermActionReasonCodeableReference(TimeStampedModel):
    """Contract term action reason codeable reference model."""

    reference = models.ForeignKey(
        ContractTermActionReasonReference,
        on_delete=models.CASCADE,
        related_name="contract_term_action_reason_codeable_reference_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_action_reason_codeable_reference_concept",
        null=True,
    )


class ContractTermAction(TimeStampedModel):
    """Contract Term Action model."""

    do_not_perform = models.BooleanField(default=False)
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_action_type",
        null=True,
    )
    subject = models.ManyToManyField(
        ContractTermActionSubject,
        related_name="contract_term_action_subject",
        blank=True,
    )
    intent = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_action_intent",
        null=True,
    )
    link_id = ArrayField(models.CharField(max_length=255), null=True)
    status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_action_status",
        null=True,
    )
    context = models.ForeignKey(
        "encounters.EncounterEpisodeOfCareReference",
        on_delete=models.CASCADE,
        related_name="contract_term_action_context",
        null=True,
    )
    context_link_id = ArrayField(models.CharField(max_length=255), null=True)
    occurrence_date_time = models.DateTimeField(null=True)
    occurrence_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="contract_term_action_occurrence_period",
        null=True,
    )
    occurrence_timing = models.ForeignKey(
        Timing,
        related_name="contract_term_action_occurrence_timing",
        on_delete=models.CASCADE,
        null=True,
    )
    requester = models.ManyToManyField(
        ContractTermActionRequesterReference,
        related_name="contract_term_action_requester",
        blank=True,
    )
    requester_link_id = ArrayField(models.CharField(max_length=255), null=True)
    performer_type = models.ManyToManyField(
        CodeableConcept,
        related_name="contract_term_action_performer_type",
        blank=True,
    )
    performer_role = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer_role",
        null=True,
    )
    performer = models.ForeignKey(
        ContractTermActionPerformerReference,
        on_delete=models.CASCADE,
        related_name="contract_term_action_performer",
        null=True,
    )
    performer_link_id = ArrayField(models.CharField(max_length=255), null=True)
    reason = models.ManyToManyField(
        ContractTermActionReasonCodeableReference,
        related_name="contract_term_action_reason",
        blank=True,
    )
    reason_link_id = ArrayField(models.CharField(max_length=255), null=True)
    note = models.ManyToManyField(
        Annotation, related_name="contract_term_action_note", blank=True
    )
    security_label_number = ArrayField(models.IntegerField(), null=True)


class ContractTerm(TimeStampedModel):
    """Contract Term model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="contract_term_identifier",
        null=True,
        on_delete=models.CASCADE,
    )
    issued = models.DateTimeField(null=True)
    applies = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="contract_term_applies",
        null=True,
    )
    topic_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_topic_codeable_concept",
        null=True,
    )
    topic_reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name="contract_term_topic_reference",
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_type",
        null=True,
    )
    sub_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_term_sub_type",
        null=True,
    )

    text = models.TextField(null=True)
    security_label = models.ManyToManyField(
        ContractTermSecurityLabel,
        related_name="contract_term_security_label",
        blank=True,
    )

    offer = models.ForeignKey(
        ContractTermOffer,
        on_delete=models.CASCADE,
        related_name="contract_term_offer",
        null=True,
    )

    asset = models.ManyToManyField(
        ContractTermAsset,
        related_name="contract_term_asset",
        blank=True,
    )
    action = models.ManyToManyField(
        ContractTermAction,
        related_name="contract_term_action",
        blank=True,
    )
    group = models.ManyToManyField(
        "self",
        blank=True,
    )


class ContractSignerPartyReference(BaseReference):
    """Contract Signer Party Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_signer_party_reference_identifier",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="contract_signer_party_reference_organization",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="contract_signer_party_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="contract_signer_party_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="contract_signer_party_reference_practitioner_role",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="contract_signer_party_reference_related_person",
        null=True,
    )


class ContractSigner(TimeStampedModel):
    """Contract Signer model."""

    type = models.ForeignKey(
        Coding,
        on_delete=models.CASCADE,
        related_name="contract_signer_type",
        null=True,
    )
    party = models.ForeignKey(
        ContractSignerPartyReference,
        on_delete=models.CASCADE,
        related_name="contract_signer_party",
        null=True,
    )
    signature = models.ManyToManyField(
        Signature,
        related_name="contract_signer_signature",
        blank=True,
    )


class ContractFriendlyContentReferenceReference(BaseReference):
    """Contract Friendly Content Reference Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_friendly_content_reference_reference_identifier",
        null=True,
    )
    # composition = models.ForeignKey(
    #     "compositions.Composition",
    #     on_delete=models.CASCADE,
    #     related_name="contract_friendly_content_reference_reference_composition",
    #     null=True,
    # )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.CASCADE,
        related_name="contract_friendly_content_reference_reference_document_reference",
        null=True,
    )
    # questionnaire_response = models.ForeignKey(
    #     "questionnaireresponses.QuestionnaireResponse",
    #     on_delete=models.CASCADE,
    #     related_name="contract_friendly_content_reference_reference_questionnaire_response",
    #     null=True,
    # )


class ContractLegalContentReferenceReference(BaseReference):
    """Contract Legal Content Reference Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_legal_content_reference_reference_identifier",
        null=True,
    )
    # composition = models.ForeignKey(
    #     "compositions.Composition",
    #     on_delete=models.CASCADE,
    #     related_name="contract_legal_content_reference_reference_composition",
    #     null=True,
    # )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.CASCADE,
        related_name="contract_legal_content_reference_reference_document_reference",
        null=True,
    )
    # questionnaire_response = models.ForeignKey(
    #     "questionnaireresponses.QuestionnaireResponse",
    #     on_delete=models.CASCADE,
    #     related_name="contract_legal_content_reference_reference_questionnaire_response",
    #     null=True,
    # )


class ContractFriendly(TimeStampedModel):
    """Contract Friendly model."""

    content_attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="contract_friendly_content_attachment",
        null=True,
    )
    content_reference = models.ForeignKey(
        ContractFriendlyContentReferenceReference,
        on_delete=models.CASCADE,
        related_name="contract_friendly_content_reference",
        null=True,
    )


class ContractLegal(TimeStampedModel):
    """Contract Legal model."""

    content_attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="contract_legal_content_attachment",
        null=True,
    )
    content_reference = models.ForeignKey(
        ContractLegalContentReferenceReference,
        on_delete=models.CASCADE,
        related_name="contract_legal_content_reference",
        null=True,
    )


class ContractRule(TimeStampedModel):
    """Contract rule model."""

    content_attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="contract_rule_content_attachment",
        null=True,
    )
    # content_reference = models.ForeignKey(
    #     "documentreferences.DocumentReferenceReference",
    #     on_delete=models.CASCADE,
    #     related_name="contract_rule_content_reference",
    #     null=True,
    # )


class ContractLegallyBindingReferenceReference(BaseReference):
    """Contract Legally Binding Reference Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_legally_binding_reference_reference_identifier",
        null=True,
    )
    # composition = models.ForeignKey(
    #     "compositions.Composition",
    #     on_delete=models.CASCADE,
    #     related_name="contract_legally_binding_reference_reference_composition",
    #     null=True,
    # )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.CASCADE,
        related_name="contract_legally_binding_reference_reference_document_reference",
        null=True,
    )
    # questionnaire_response = models.ForeignKey(
    #     "questionnaireresponses.QuestionnaireResponse",
    #     on_delete=models.CASCADE,
    #     related_name="contract_legally_binding_reference_reference_questionnaire_response",
    #     null=True,
    # )
    contract = models.ForeignKey(
        "Contract",
        on_delete=models.CASCADE,
        related_name="contract_legally_binding_reference_reference_contract",
        null=True,
    )


class Contract(TimeStampedModel):
    """Contract model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="contract_identifier",
        blank=True,
    )
    url = models.URLField(null=True)
    version = models.CharField(max_length=255, null=True)
    status = models.CharField(
        max_length=255, null=True, choices=choices.ContractStatusChoices.choices
    )
    legal_state = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_legal_state",
        null=True,
    )
    instantiates_canonical = models.ForeignKey(
        "ContractReference",
        on_delete=models.CASCADE,
        related_name="contract_instantiates_canonical",
        null=True,
    )
    instantiates_uri = models.URLField(null=True)
    content_derivative = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_content_derivative",
        null=True,
    )
    issued = models.DateTimeField(null=True)
    applies = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="contract_applies",
        null=True,
    )
    expiration_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_expiration_type",
        null=True,
    )
    subject = models.ManyToManyField(
        ContractSubjectReference,
        related_name="contract_subject",
        blank=True,
    )
    authority = models.ManyToManyField(
        OrganizationReference,
        related_name="contract_authority",
        blank=True,
    )
    domain = models.ManyToManyField(
        "locations.LocationReference",
        related_name="contract_domain",
        blank=True,
    )
    site = models.ManyToManyField(
        "locations.LocationReference",
        related_name="contract_site",
        blank=True,
    )
    name = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255, null=True)
    subtitle = models.CharField(max_length=255, null=True)
    alias = ArrayField(models.CharField(max_length=255), null=True)
    author = models.ForeignKey(
        ContractAuthorReference,
        on_delete=models.CASCADE,
        related_name="contract_author",
        null=True,
    )
    scope = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_scope",
        null=True,
    )
    topic_codeable_concept = models.ManyToManyField(
        CodeableConcept,
        related_name="contract_topic_codeable_concept",
        blank=True,
    )
    topic_reference = models.ManyToManyField(
        Reference,
        related_name="contract_topic_reference",
        blank=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="contract_type",
        null=True,
    )
    sub_type = models.ManyToManyField(
        CodeableConcept,
        related_name="contract_sub_type",
        blank=True,
    )
    content_definition = models.ForeignKey(
        ContractContentDefinition,
        on_delete=models.CASCADE,
        related_name="contract_content_definition",
        null=True,
    )
    term = models.ManyToManyField(
        ContractTerm,
        related_name="contract_term",
        blank=True,
    )
    supporting_info = models.ManyToManyField(
        Reference,
        related_name="contract_supporting_info",
        blank=True,
    )
    relevant_history = models.ManyToManyField(
        "provenances.ProvenanceReference",
        related_name="contract_relevant_history",
        blank=True,
    )
    signer = models.ManyToManyField(
        ContractSigner,
        related_name="contract_signer",
        blank=True,
    )
    friendly = models.ManyToManyField(
        ContractFriendly,
        related_name="contract_friendly",
        blank=True,
    )
    legal = models.ManyToManyField(
        ContractLegal,
        related_name="contract_legal",
        blank=True,
    )
    rule = models.ManyToManyField(
        ContractRule,
        related_name="contract_rule",
        blank=True,
    )
    legally_binding_attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="contract_legally_binding_attachment",
        null=True,
    )
    legally_binding_reference = models.ForeignKey(
        ContractLegallyBindingReferenceReference,
        on_delete=models.CASCADE,
        related_name="contract_legally_binding_reference",
        null=True,
    )


class ContractReference(BaseReference):
    """Contract reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="contract_reference_identifier",
        null=True,
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="contract_reference_contract",
        null=True,
    )
