"""Choices for organizations."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class OrganizationStatus(models.TextChoices):
    """Eligibility code choices."""

    PENDING = "pending", _("Pending")
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")


class OrganizationType(models.TextChoices):
    """Eligibility code choices."""

    HEALTHCARE_PROVIDER = "healthcare_provider", _("Healthcare Provider")
    HOSPITAL_DEPARTMENT = "hospital_department", _("Hospital Department")
    ORGANIZATIONAL_TEAM = "organizational_team", _("Organizational Team")
    GOVERNMENT = "government", _("Government")
    INSURANCE_COMPANY = "insurance_company", _("Insurance Company")
    PAYER = "payer", _("Payer")
    EDUCATIONAL_INSTITUTE = "educational_institute", _("Educational Institute")
    RELIGIOUS_INSTITUTION = "religious_institution", _("Religious Institution")
    CLINICAL_RESEARCH_SPOONSOR = (
        "clinical_research_sponsor",
        _("Clinical Research Sponsor"),
    )
    COMMUNITY_GROUP = "community_group", _("Community Group")
    NON_HEALTHCARE_PROVIDER = "non_healthcare_provider", _("Non Healthcare Provider")
    OTHER = "other", _("Other")
