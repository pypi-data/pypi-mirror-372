"""Schedule serializers."""

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
)
from dfhir.healthcareservices.serializers import (
    HealthCareServiceCodeableReferenceSerializer,
)
from dfhir.schedules.models import Schedule, ScheduleReference, SchedulesActorReference


class ActorSerializer(BaseReferenceModelSerializer):
    """Actor serializer."""

    class Meta:
        """Meta class."""

        model = SchedulesActorReference
        exclude = ["created_at", "updated_at"]


class ScheduleSerializer(BaseWritableNestedModelSerializer):
    """Schedule serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    actor = ActorSerializer(many=True, required=True)
    planning_horizon = PeriodSerializer(many=False, required=False)
    service_type = HealthCareServiceCodeableReferenceSerializer(
        many=True, required=False
    )
    specialty = CodeableConceptSerializer(many=True, required=False)
    service_category = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Schedule
        exclude = ["created_at", "updated_at"]

    # TODO: This needs to be moved
    # def validate(self, data):
    #     """Validate data."""
    #     validate_date_time_fields(
    #         data.get("start_date_time"), data.get("end_date_time")
    #     )
    #     return data


class ScheduleReferenceSerializer(BaseReferenceModelSerializer):
    """Schedule reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ScheduleReference
        exclude = ["created_at", "updated_at"]
