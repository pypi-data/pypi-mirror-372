"""Practitioner-related choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ServiceModeChoices(models.TextChoices):
    """Service mode choices."""

    IN_PERSON = "in_person", _("in-person")
    TELEPHONE = "telephone", _("telephone")
    VIDEO_CONFERENCE = "video_conference", _("video-conference")
    CHAT = (
        "chat",
        _("chat"),
    )
