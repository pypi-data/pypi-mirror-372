"""Location admin."""

from django.contrib import admin

from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Location admin."""

    list_display = (
        "name",
        "status",
        "alias",
    )
    search_fields = (
        "name",
        "status",
        "alias",
    )
