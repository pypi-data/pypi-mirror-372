"""Base models for the dfhir app."""

from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db import models

from . import choices

PHONE_REGEX = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)


class TimeStampedModel(models.Model):
    """An abstract base class model that provides self-updating 'created' and 'modified' fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def resource_type(self):
        """Return the resource type."""
        return self.__class__.__name__

    class Meta:
        """Meta options."""

        abstract = True


class BaseReference(TimeStampedModel):
    """Base reference class."""

    reference = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=255, null=True)
    identifier = models.ForeignKey("Identifier", on_delete=models.DO_NOTHING, null=True)
    display = models.CharField(max_length=255, null=True)

    class Meta:
        """Meta options."""

        abstract = True


class Reference(BaseReference):
    """Reference model."""


class Period(TimeStampedModel):
    """Period model."""

    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)


class ServiceType(TimeStampedModel):
    """ServiceType model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)

    class Meta:
        """Meta options."""

        app_label = "healthcareservices"


class ContactPoint(TimeStampedModel):
    """ContactPoint model."""

    system = models.CharField(
        max_length=10,
        choices=choices.ContactPointSystemChoices.choices,
        blank=True,
        null=True,
        help_text="Telecommunications form for contact point.",
    )
    value = models.CharField(max_length=255, blank=True, null=True)
    use = models.CharField(
        max_length=10,
        choices=choices.ContactPointUseChoices.choices,
        blank=True,
        null=True,
    )
    rank = models.PositiveIntegerField(blank=True, null=True)
    period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="contact_point_period",
        null=True,
    )


class Telecom(TimeStampedModel):
    """Telecom model."""

    value = models.CharField(validators=[PHONE_REGEX], max_length=17, blank=True)
    use = models.CharField(
        max_length=10, choices=choices.TelecomUseChoices.choices, default="mobile"
    )

    class Meta:
        """Meta options."""

        abstract = True


class Address(TimeStampedModel):
    """Address model."""

    use = models.CharField(
        max_length=10, choices=choices.AddressUseChoices.choices, null=True
    )
    type = models.CharField(
        max_length=10, choices=choices.AddressTypeChoices.choices, null=True
    )
    text = models.CharField(max_length=255, null=True, blank=True)
    line = ArrayField(
        models.CharField(max_length=255, null=True, blank=True), null=True
    )
    city = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    period = models.ForeignKey(
        Period, on_delete=models.DO_NOTHING, related_name="address_period", null=True
    )


class ContactDetail(TimeStampedModel):
    """ContactDetail model."""

    name = models.CharField(max_length=255, null=True, blank=True)
    telecom = models.ManyToManyField(
        ContactPoint, related_name="contact_detail_telecom", blank=True
    )


class AvailableTime(TimeStampedModel):
    """AvailableTime model."""

    days_of_week = ArrayField(
        models.CharField(max_length=255, choices=choices.DaysOfWeekChoices.choices),
        null=True,
    )
    all_day = models.BooleanField(default=False)
    available_start_time = models.TimeField(null=True)
    available_end_time = models.TimeField(null=True)


class NotAvailableTime(TimeStampedModel):
    """NotAvailableTime model."""

    description = models.CharField(max_length=255, null=True, blank=True)
    during = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="not_available_time_during",
        null=True,
    )


class Availability(TimeStampedModel):
    """Availability model."""

    period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="availability_period",
        null=True,
    )
    available_time = models.ManyToManyField(
        AvailableTime, related_name="availability_available_time", blank=True
    )
    not_available_time = models.ManyToManyField(
        NotAvailableTime, related_name="availability_not_available_time", blank=True
    )


class HumanName(TimeStampedModel):
    """HumanName model."""

    use = models.CharField(
        max_length=255, choices=choices.HumanNameUseChoices.choices, null=True
    )
    text = models.TextField(null=True)
    family = models.CharField(max_length=255, null=True)
    given = ArrayField(models.CharField(max_length=255), null=True)
    prefix = ArrayField(models.CharField(max_length=255), null=True)
    suffix = ArrayField(models.CharField(max_length=255), null=True)
    period = models.ForeignKey(
        Period, on_delete=models.DO_NOTHING, related_name="human_name_period", null=True
    )


class ExtendedContactDetail(TimeStampedModel):
    """ExtendedContactDetail model."""

    system = models.CharField(
        max_length=10,
        choices=choices.TelecomSystemChoices.choices,
        blank=True,
        null=True,
        help_text="Telecommunications form for contact point.",
    )
    purpose = models.ForeignKey(
        "CodeableConcept",
        on_delete=models.DO_NOTHING,
        related_name="extended_contact_detail_purpose",
        null=True,
    )
    name = models.ManyToManyField(
        HumanName, related_name="extended_contact_detail_name", blank=True
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.DO_NOTHING,
        related_name="extended_contact_detail_address",
        null=True,
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="extended_contact_detail_period",
        null=True,
    )
    telecom = models.ManyToManyField(
        ContactPoint, related_name="extended_contact_detail_telecom", blank=True
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="extended_contact_detail_organization",
        null=True,
    )


class Participant(TimeStampedModel):
    """Participants involved in the appointment."""

    type = models.CharField(
        max_length=255, choices=choices.ParticipantType.choices, null=True
    )
    status = models.CharField(
        max_length=255, choices=choices.ParticipantStatus.choices, null=True
    )

    class Meta:
        """Meta options."""

        abstract = True


class Attachment(TimeStampedModel):
    """diagnostic report attachment model."""

    title = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=255, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    size = models.BigIntegerField(blank=True, null=True)
    hash = models.BinaryField(blank=True, null=True)
    creation = models.DateTimeField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    width = models.PositiveIntegerField(blank=True, null=True)
    frames = models.PositiveIntegerField(blank=True, null=True)
    duration = models.DecimalField(
        max_digits=1000, decimal_places=2, blank=True, null=True
    )
    pages = models.PositiveIntegerField(blank=True, null=True)


class Coding(TimeStampedModel):
    """Coding model."""

    system = models.CharField(max_length=255, null=True)
    version = models.CharField(max_length=255, null=True)
    code = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255, null=True)
    user_selected = models.BooleanField(default=False)


class CodeableConcept(TimeStampedModel):
    """CodeableConcept model."""

    text = models.CharField(max_length=255, null=True)
    coding = models.ManyToManyField(Coding, related_name="codeable_concept")


class OrganizationReference(BaseReference):
    """Organization Reference model."""

    identifier = models.ForeignKey(
        "Identifier",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="organization_reference_identifier",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="organization_reference",
        null=True,
    )


class Identifier(TimeStampedModel):
    """Identifier model."""

    use = models.CharField(max_length=255, null=True)
    type = models.ForeignKey(CodeableConcept, on_delete=models.DO_NOTHING, null=True)
    system = models.CharField(max_length=255, null=True)
    value = models.CharField(max_length=255, null=True)
    period = models.ForeignKey(
        Period, on_delete=models.DO_NOTHING, related_name="identifier", null=True
    )
    assigner = models.ForeignKey(
        "organizationReference",
        on_delete=models.DO_NOTHING,
        related_name="identifier_for_organization",
        null=True,
    )


class Qualification(TimeStampedModel):
    """Qualification model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="qualification_identifier", blank=True
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="qualification_code",
        null=True,
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="qualification_period",
        null=True,
    )
    issuer = models.ForeignKey(
        "OrganizationReference",
        on_delete=models.DO_NOTHING,
        related_name="qualification_issuer",
        null=True,
    )


class ConnectionType(TimeStampedModel):
    """ConnectionType model."""

    code = models.CharField(max_length=255, null=True)
    system = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255, null=True)
    definition = models.TextField(null=True)


class Payload(TimeStampedModel):
    """Payload model."""

    type = models.ManyToManyField(
        CodeableConcept, related_name="payload_type", blank=True
    )
    # mimetype = models.CharField(max_length=255, null=True) #TODO: needs a revisit
    profile_uri = ArrayField(models.URLField(max_length=255), null=True)
    profile_canonical = ArrayField(models.URLField(max_length=255), null=True)


class VirtualServiceDetailAddress(TimeStampedModel):
    """Connection details of a virtual service (e.g. conference call)."""

    address_url = models.URLField(max_length=255, null=True)
    address_string = models.TextField(null=True)
    address_contact_point = models.ForeignKey(
        ContactPoint,
        on_delete=models.DO_NOTHING,
        related_name="virtual_service_detail_address_contact_point",
        null=True,
    )
    address_extended_contact_detail = models.ForeignKey(
        ExtendedContactDetail,
        on_delete=models.DO_NOTHING,
        related_name="virtual_service_detail_address_extended_contact_detail",
        null=True,
    )


class VirtualServiceDetails(TimeStampedModel):
    """Connection details of a virtual service (e.g. conference call)."""

    channel_type = models.ForeignKey(
        Coding,
        on_delete=models.DO_NOTHING,
        related_name="virtual_service_details_channel_type",
        null=True,
    )
    address = models.ForeignKey(
        VirtualServiceDetailAddress,
        on_delete=models.DO_NOTHING,
        related_name="virtual_service_details_address",
        null=True,
    )
    additional_info = ArrayField(models.URLField(max_length=255), null=True)
    max_participants = models.PositiveIntegerField(null=True)
    session_key = models.CharField(max_length=255, null=True)


class Quantity(TimeStampedModel):
    """Quantity model."""

    value = models.DecimalField(max_digits=1000, decimal_places=2, null=True)
    comparator = models.CharField(
        max_length=255, choices=choices.QuantityComparatorChoices.choices, null=True
    )
    unit = models.CharField(max_length=255, null=True)
    system = models.CharField(max_length=255, null=True)
    code = models.CharField(max_length=255, null=True)


class Range(TimeStampedModel):
    """Range model."""

    low = models.ForeignKey(
        Quantity, on_delete=models.DO_NOTHING, related_name="range_low", null=True
    )
    high = models.ForeignKey(
        Quantity, on_delete=models.DO_NOTHING, related_name="range_high", null=True
    )


class Annotation(TimeStampedModel):
    """Annotation model."""

    author_reference = models.ForeignKey(
        Reference,
        on_delete=models.DO_NOTHING,
        related_name="annotation_author_reference",
        null=True,
    )
    author_string = models.CharField(max_length=255, null=True)
    time = models.DateTimeField(null=True)
    text = models.TextField(null=True)


class Communication(TimeStampedModel):
    """communication model."""

    language = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="communication_language",
        null=True,
    )
    preferred = models.BooleanField(default=False)


class Ratio(TimeStampedModel):
    """ratio model."""

    numerator = models.ForeignKey(
        Quantity, on_delete=models.DO_NOTHING, null=True, related_name="ratio_numerator"
    )
    denominator = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="ratio_denominator",
    )


class CodeableReference(TimeStampedModel):
    """codeable reference."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="codeable_reference_concept",
    )
    reference = models.ForeignKey(
        Reference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="codeable_reference_reference",
    )


class Repeat(TimeStampedModel):
    """repeat model."""

    bounds_duration = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="repeat_bounds_duration",
        null=True,
    )
    bounds_range = models.ForeignKey(
        Range,
        on_delete=models.DO_NOTHING,
        related_name="repeat_bounds_range",
        null=True,
    )
    bounds_period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="repeat_bounds_period",
        null=True,
    )
    count = models.PositiveIntegerField(null=True)
    count_max = models.PositiveIntegerField(null=True)
    duration = models.DecimalField(null=True, max_digits=1000, decimal_places=2)
    duration_max = models.DecimalField(null=True, max_digits=1000, decimal_places=2)
    duration_unit = models.CharField(
        max_length=255, null=True, choices=choices.RepeatDurationUnits.choices
    )
    frequency = models.PositiveIntegerField(null=True)
    frequency_max = models.PositiveIntegerField(null=True)
    period = models.DecimalField(null=True, max_digits=1000, decimal_places=2)
    period_max = models.DecimalField(null=True, max_digits=1000, decimal_places=2)
    period_unit = models.CharField(
        max_length=255, null=True, choices=choices.RepeatDurationUnits.choices
    )
    day_of_week = models.ManyToManyField(
        Coding,
        blank=True,
        related_name="repeat_day_of_week",
    )
    time_of_day = models.TimeField(null=True)
    when = models.ManyToManyField(Coding, blank=True, related_name="repeat_when")


class Timing(TimeStampedModel):
    """timing model."""

    event = models.DateTimeField(null=True)
    repeat = models.ForeignKey(
        Repeat, on_delete=models.DO_NOTHING, null=True, related_name="timing_repeat"
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="timing_code",
    )


class RelatedArtifact(TimeStampedModel):
    """RelatedArtifact model."""

    type = models.CharField(
        max_length=255, choices=choices.RelatedArtifactTypeChoices.choices, null=True
    )
    classifier = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="related_artifact_classifier",
        null=True,
    )
    label = models.CharField(max_length=255, null=True)

    display = models.TextField(null=True)
    citation = models.TextField(null=True)
    document = models.ForeignKey(
        Attachment,
        on_delete=models.DO_NOTHING,
        related_name="related_artifact_document",
        null=True,
    )
    # resource = models.ForeignKey(  # TODO: this should be canonical
    #     Reference,
    #     on_delete=models.DO_NOTHING,
    #     related_name="related_artifact_resource",
    #     null=True,
    # )
    resource_reference = models.ForeignKey(
        Reference,
        on_delete=models.DO_NOTHING,
        related_name="related_artifact_resource",
        null=True,
    )
    publication_status = models.CharField(
        max_length=255, null=True, choices=choices.PublicationStatusChoices.choices
    )
    publication_date = models.DateTimeField(null=True)


class UsageContext(TimeStampedModel):
    """UsageContext model."""

    code = models.ForeignKey(
        Coding,
        on_delete=models.DO_NOTHING,
        related_name="usage_context_code",
        null=True,
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="usage_context_value",
        null=True,
    )
    value_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="usage_context_value_quantity",
        null=True,
    )
    value_range = models.ForeignKey(
        Range,
        on_delete=models.DO_NOTHING,
        related_name="usage_context_value_range",
        null=True,
    )
    # value_reference = models.ForeignKey(
    #     Reference,
    #     on_delete=models.DO_NOTHING,
    #     related_name="usage_context_value_reference",
    #     null=True,
    # )


class ProductShelfLife(TimeStampedModel):
    """ProductShelfLife model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="product_shelf_life_type",
        null=True,
    )
    period_duration = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="product_shelf_life_period_duration",
        null=True,
    )
    period_string = models.CharField(max_length=255, null=True)
    special_precautions_for_storage = models.ManyToManyField(
        CodeableConcept,
        related_name="product_shelf_life_special_precautions_for_storage",
        blank=True,
    )


class Expression(TimeStampedModel):
    """Expression model."""

    description = models.TextField(null=True)
    name = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=255, null=True)
    expression = models.TextField(null=True)
    reference = models.CharField(max_length=255, null=True)


class RelativeTime(TimeStampedModel):
    """Relative time model."""

    context_reference = models.ForeignKey(
        Reference,
        on_delete=models.DO_NOTHING,
        related_name="relative_time_context_reference",
        null=True,
    )
    # TODO: fix this
    # context_definition = models.ForeignKey(CodeableConcept, on_delete=models.DO_NOTHING, related_name="relative_time_context_definition", null=True)
    context_path = models.CharField(max_length=255, null=True)
    context_code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="relative_time_context_code",
        null=True,
    )
    offset_duration = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="relative_time_offset_duration",
        null=True,
    )
    offset_range = models.ForeignKey(
        Range,
        on_delete=models.DO_NOTHING,
        related_name="relative_time_offset_range",
        null=True,
    )
    text = models.TextField(null=True)


class Age(Quantity):
    """Age model."""

    pass


class Duration(Quantity):
    """Duration model."""

    pass


class SimpleQuantity(Quantity):
    """SimpleQuantity model."""

    pass


class Money(TimeStampedModel):
    """Money model."""

    value = models.DecimalField(max_digits=1000, decimal_places=2, null=True)
    currency = models.CharField(max_length=255, null=True)


class MonetaryComponent(TimeStampedModel):
    """MonetaryComponent model."""

    type = models.CharField(
        max_length=255, null=True, choices=choices.MonetaryComponentChoices.choices
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="monetory_component_code",
        null=True,
    )
    factor = models.DecimalField(max_digits=1000, decimal_places=2, null=True)
    amount = models.ForeignKey(
        Money,
        on_delete=models.DO_NOTHING,
        related_name="monetory_component_amount",
        null=True,
    )


class SignatureWhoReference(BaseReference):
    """Signature who reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="signature_who_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="signature_who_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="signature_who_reference_practitioner_role",
        null=True,
    )
    related_person = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="signature_who_reference_related_person",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="signature_who_reference_patient",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        related_name="signature_who_reference_device",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="signature_who_reference_organization",
        null=True,
    )


class SignatureOnBehalfOfReference(BaseReference):
    """Signature on behalf of reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="signature_on_behalf_of_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="signature_on_behalf_of_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="signature_on_behalf_of_reference_practitioner_role",
        null=True,
    )
    related_person = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="signature_on_behalf_of_reference_related_person",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="signature_on_behalf_of_reference_patient",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        related_name="signature_on_behalf_of_reference_device",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="signature_on_behalf_of_reference_organization",
        null=True,
    )


class Signature(TimeStampedModel):
    """Signature model."""

    type = models.ManyToManyField(Coding, related_name="signature_type", blank=True)
    when = models.DateTimeField(null=True)
    who = models.ForeignKey(
        SignatureWhoReference,
        on_delete=models.DO_NOTHING,
        related_name="signature_who",
        null=True,
    )
    on_behalf_of = models.ForeignKey(
        SignatureOnBehalfOfReference,
        on_delete=models.DO_NOTHING,
        related_name="signature_on_behalf_of",
        null=True,
    )
    target_format = models.CharField(max_length=255, null=True)
    sig_format = models.CharField(max_length=255, null=True)
    data = models.TextField(null=True)


class TriggerDefinition(TimeStampedModel):
    """TriggerDefinition model."""

    type = models.CharField(
        max_length=255, choices=choices.TriggerDefinitionTypeChoices.choices, null=True
    )
    name = models.CharField(max_length=255, null=True)
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="trigger_definition_code",
        null=True,
    )
    # subscription_topic = models.ForeignKey(
    #     CanonicalSubscriptionTopic,
    #     on_delete=models.DO_NOTHING,
    #     related_name="trigger_definition_subscription_topic",
    #     null=True,
    # )
    timing_timing = models.ForeignKey(
        Timing,
        on_delete=models.DO_NOTHING,
        related_name="trigger_definition_timing_timing",
        null=True,
    )
    timing_reference = models.ForeignKey(
        "schedules.ScheduleReference",
        on_delete=models.DO_NOTHING,
        related_name="trigger_definition_timing_reference",
        null=True,
    )
    timing_date = models.DateField(null=True)
    timing_date_time = models.DateTimeField(null=True)
    # data = models.ForeignKey(
    #     "DataRequirement",
    #     on_delete=models.DO_NOTHING,
    #     related_name="trigger_definition_data",
    #     null=True,
    # )
    condition = models.ForeignKey(
        Expression,
        on_delete=models.DO_NOTHING,
        related_name="trigger_definition_condition",
        null=True,
    )


# class DataRequirement(TimeStampedModel):
#     """DataRequirement model."""
#
#     type = models.CharField(max_length=255, null=True)
#     # profile = models.ManyToManyField(
#     #     CanonicalStructureDefinition, related_name="data_requirement_profile", blank=True
#     # )
#     subject_codeable_concept = models.ForeignKey(
#         CodeableConcept,
#         on_delete=models.DO_NOTHING,
#         related_name="data_requirement_subject_codeable_concept",
#         null=True,
#     )
#     subject_reference = models.ForeignKey(
#         "groups.GroupReference",
#         on_delete=models.DO_NOTHING,
#         related_name="data_requirement_subject_reference",
#         null=True,
#     )
#     must_support = ArrayField(models.CharField(max_length=255), null=True)
