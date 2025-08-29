"""payment reconciliations app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PaymentreconciliationsConfig(AppConfig):
    """payment reconciliations app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.paymentreconciliations"
    verbose_name = _("Payment Reconciliations")
