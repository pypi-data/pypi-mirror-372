"""Healthcare Services Choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class EligibilityCode(models.TextChoices):
    """Eligibility code choices."""

    VETERANS = "veterans", _("Veterans")
    NEW_PATIENT = "new_patient", _("New Patient")
    PADIATIC_PATIENT = "padiatic_patient", _("Padiatic Patient")
    LOW_INCOME_PATEINT = "low_income_patient", _("Low Income Patient")
    UNINSURED_PATIENT = "uninsure_patient", _("Uninsured Patient")
    RENAL_PATIENT = "renal_patient", _("Renal Patient")
    SPECIALIT_REFERAL_REQUIRED = (
        "specialist_referral_required",
        _("Specialist Referral Required"),
    )
    ASSESSMENT_REQUIRED = "assessment_required", _("Assessment Required")


class ServiceProvisionCode(models.TextChoices):
    """Service provision code choices."""

    FREE = "free", _("Free")
    DISCOUNTED = "discounted", _("Discounted")
    FEE_APPLY = "fee_apply", _("Fee Apply")


class ServiceModeChoices(models.TextChoices):
    """Service mode choices."""

    TELEPHONE = "telephone", _("Telephone")
    IN_PERSON = "in_person", _("In Person")
    VIDEO_CONFERENCE = "video_conference", _("Video Conference")
    CHAT = "chat", _("Chat")


class ReferralMethodChoices(models.TextChoices):
    """Referral method choices."""

    FAX = "fax", _("Fax")
    SECURE_EMAIL = "secure_email", _("Secure Email")
    PHONE = "phone", _("Phone")
    URL = "url", _("URL")
    SECURE_MESSAGING = "secure_messaging", _("Secure Messaging")
    MAIL = "mail", _("Mail")
    SELF_REFERRAL = "self_referral", _("Self Referral")
