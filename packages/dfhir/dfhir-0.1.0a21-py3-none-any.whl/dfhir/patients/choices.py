"""Patient-related choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactRelationshipChoices(models.TextChoices):
    """Contact relationship choices."""

    BILLING_CONTACT_PERSON = "billing_contact_person", _("billing-contact-person")
    CONTACT_PERSON = "contact_person", _("contact-person")
    EMERGENCY_CONTACT_PERSON = "emergency_contact_person", _("emergency-contact-person")
    PERSON_PREPARING_REFERRAL = (
        "person_preparing_referral",
        _("person-preparing-referral"),
    )
    EMPLOYER = "employer", _("employer")
    EMERGENCY_CONTACT = "emergency_contact", _("emergency-contact")
    FEDERAL_AGENCY = "federal_agency", _("federal-agency")
    INSURANCE_COMPANY = "insurance_company", _("insurance-company")
    NEXT_OF_KIN = "next_of_kin", _("next-of-kin")
    STATE_AGENCY = "state_agency", _("state-agency")
    UNKNOWN = "unknown", _("unknown")


class PatientLinkChoices(models.TextChoices):
    """Patient link choices."""

    REPLACED_BY = "replaced_by", _("replaced-by")
    REPLACES = "replaces", _("replaces")
    REFER = "refer", _("refer")
    SEEALSO = "seealso", _("seealso")
