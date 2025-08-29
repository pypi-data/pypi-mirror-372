"""Schedule filters module."""

from django_filters import DateTimeFromToRangeFilter
from django_filters import rest_framework as filters

from .models import Schedule


class ScheduleFilter(filters.FilterSet):
    """Schedule filter."""

    start_date_time = DateTimeFromToRangeFilter(field_name="start_date_time")
    end_date_time = DateTimeFromToRangeFilter(field_name="end_date_time")
    practitioner = filters.CharFilter(field_name="practitioner")

    class Meta:
        """Schedule filter meta class."""

        model = Schedule
        fields = ["start_date_time", "end_date_time", "practitioner"]
