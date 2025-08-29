"""Encounter filter module."""

from django_filters import DateTimeFromToRangeFilter
from django_filters import rest_framework as filters

from .models import Encounter


class EncounterFilter(filters.FilterSet):
    """Encounter filter."""

    id = filters.CharFilter(field_name="id", lookup_expr="iexact")
    start_date_time = DateTimeFromToRangeFilter(
        field_name="start_date_time", lookup_expr="gte"
    )
    end_date_time = DateTimeFromToRangeFilter(
        field_name="end_date_time", lookup_expr="lte"
    )
    subject = filters.CharFilter(method="patient_filter", lookup_expr="icontains")
    participant = filters.CharFilter(method="practitioner_filter", lookup_expr="iexact")

    def practitioner_filter(self, querryset, name, value):
        """Filter participant by practitioner ID."""
        if value:
            return querryset.filter(participant__actor__practitioner=value)
        return querryset

    def patient_filter(self, querryset, name, value):
        """Filter participant by patient ID."""
        if value:
            return querryset.filter(subject__patient=value)
        return querryset

    class Meta:
        """Meta class."""

        model = Encounter
        fields = ["id", "start_date_time", "end_date_time", "subject", "participant"]
