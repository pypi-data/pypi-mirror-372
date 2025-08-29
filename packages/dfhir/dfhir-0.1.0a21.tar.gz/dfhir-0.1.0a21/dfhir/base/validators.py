"""Base validators for the dfhir app."""

from django.utils import timezone
from rest_framework import serializers


def validate_date_time_fields(start_date_time, end_date_time):
    """Validate date time fields."""
    if start_date_time and end_date_time and start_date_time > end_date_time:
        raise serializers.ValidationError(
            {"start_date_time": "Start date time must be before end date time"}
        )
    if start_date_time and start_date_time < timezone.now():
        raise serializers.ValidationError(
            {"start_date_time": "Start date time must be in the future"}
        )
    if end_date_time and end_date_time < timezone.now():
        raise serializers.ValidationError(
            {"end_date_time": "End date time must be in the future"}
        )
