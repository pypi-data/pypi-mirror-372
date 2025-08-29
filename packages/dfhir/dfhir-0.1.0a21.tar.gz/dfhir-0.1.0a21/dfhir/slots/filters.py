"""Slots filters module."""

from django_filters import DateTimeFromToRangeFilter
from django_filters import rest_framework as filters

from .models import Slot


class SlotsFilter(filters.FilterSet):
    """Slots filter."""

    start_date_time = DateTimeFromToRangeFilter(field_name="start_date_time")
    end_date_time = DateTimeFromToRangeFilter(field_name="end_date_time")
    status = filters.CharFilter(field_name="status")
    practitioner = filters.CharFilter(field_name="practitioner")

    class Meta:
        """Meta class."""

        model = Slot
        fields = ["start_date_time", "end_date_time", "status", "practitioner"]
