"""Location filters."""

from django_filters import rest_framework as filters

from dfhir.locations.models import Location


class LocationFilter(filters.FilterSet):
    """Location filter."""

    name = filters.CharFilter(lookup_expr="icontains")
    location_status = filters.CharFilter(lookup_expr="icontains")
    organization = filters.CharFilter(field_name="organizations")
    service = filters.CharFilter(field_name="location_service_type")

    class Meta:
        """Meta class."""

        model = Location
        fields = ["name", "location_status"]
