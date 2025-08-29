"""Practitioner filters."""

from django_filters import rest_framework as filters

from dfhir.practitioners.models import Practitioner


class PractitionerFilter(filters.FilterSet):
    """Practitioner filter."""

    user = filters.CharFilter(field_name="user")

    class Meta:
        """Meta class."""

        model = Practitioner
        fields = ["gender", "active"]
