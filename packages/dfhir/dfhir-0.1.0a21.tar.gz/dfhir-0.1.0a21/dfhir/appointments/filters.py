"""appointment filters."""

from django_filters import DateFromToRangeFilter
from django_filters import rest_framework as filters

from dfhir.appointments.models import Appointment


class AppointmentFilter(filters.FilterSet):
    """appointment filter."""

    id = filters.CharFilter(field_name="id", lookup_expr="iexact")
    status = filters.CharFilter(field_name="status", lookup_expr="icontains")
    start = DateFromToRangeFilter(field_name="start", lookup_expr="gte")
    end = DateFromToRangeFilter(field_name="end", lookup_expr="lte")
    subject = filters.CharFilter(method="patient_filter")
    participant = filters.CharFilter(method="practitioner_filter")

    def patient_filter(self, querryset, name, value):
        """Filter subject using patient ID."""
        if value:
            return querryset.filter(subject__patient=value)
        return querryset

    def practitioner_filter(self, querryset, name, value):
        """Filter participant using practitioner ID."""
        if value:
            return querryset.filter(participant__actor__practitioner=value)
        return querryset

    class Meta:
        """meta options."""

        model = Appointment
        fields = [
            "id",
            "status",
            "start",
            "end",
            "subject",
            "participant",
        ]
