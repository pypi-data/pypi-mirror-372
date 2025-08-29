"""Contract choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ContractStatusChoices(models.TextChoices):
    """Contract status choices."""

    AMENDED = "amended", _("Amended")
    APPENDED = "appended", _("Appended")
    CANCELLED = "cancelled", _("Cancelled")
    DISPUTED = "disputed", _("Disputed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    EXECUTED = "executed", _("Executed")
    EXECUTABLE = "executable", _("Executable")
    NEGOTIABLE = "negotiable", _("Negotiable")
    OFFERED = "offered", _("Offered")
    REJECTED = "rejected", _("Rejected")
    RENEWED = "renewed", _("Renewed")
    REVOKED = "revoked", _("Revoked")
    RESOLVED = "resolved", _("Resolved")
    TERMINATED = "terminated", _("Terminated")


class ContractContentDefinitionPublicationStatusChoices(models.TextChoices):
    """Contract content definition publication status choices."""

    AMENDED = "amended", _("Amended")
    APPENDED = "appended", _("Appended")
    CANCELLED = "cancelled", _("Cancelled")
    DISPUTED = "disputed", _("Disputed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    EXECUTED = "executed", _("Executed")
    EXECUTABLE = "executable", _("Executable")
    NEGOTIABLE = "negotiable", _("Negotiable")
    OFFERED = "offered", _("Offered")
    REJECTED = "rejected", _("Rejected")
    RENEWED = "renewed", _("Renewed")
    REVOKED = "revoked", _("Revoked")
    RESOLVED = "resolved", _("Resolved")
    TERMINATED = "terminated", _("Terminated")
