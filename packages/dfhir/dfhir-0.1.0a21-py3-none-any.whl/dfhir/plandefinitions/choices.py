"""Plandefinitions choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class PlanDefinitionStatus(models.TextChoices):
    """PlanDefinition status choices."""

    ACTIVE = "active", _("Active")
    DRAFT = "draft", _("Draft")
    RETIRED = "retired", _("Retired")
    UNKNOWN = "unknown", _("Unknown")


class PlanDefinitionActionPriority(models.TextChoices):
    """PlanDefinition action priority choices."""

    ROUTINE = "routine", _("Routine")
    URGENT = "urgent", _("Urgent")
    ASAP = "asap", _("As soon as possible")
    STAT = "stat", _("Stat")


class PlanDefinitionActionGroupingBehavior(models.TextChoices):
    """PlanDefinition action grouping behavior choices."""

    VISUAL_GROUP = "visual-group", _("Visual Group")
    LOGICAL_GROUP = "logical-group", _("Logical Group")
    SENTENCE_GROUP = "sentence-group", _("Sentence Group")


class PlanDefinitionActionSelectionBehavior(models.TextChoices):
    """PlanDefinition action selection behavior choices."""

    ANY = "any", _("Any")
    ALL = "all", _("All")
    ALL_OR_NONE = "all-or-none", _("All or None")
    EXACTLY_ONE = "exactly-one", _("Exactly One")
    AT_MOST_ONE = "at-most-one", _("At Most One")
    ONE_OR_MORE = "one-or-more", _("One or More")


class PlanDefinitionActionRequiredBehavior(models.TextChoices):
    """PlanDefinition action required behavior choices."""

    MUST = "must", _("Must")
    COULD = "could", _("Could")
    MUST_UNLESS_DOCUMENTED = "must-unless-documented", _("Must unless Documented")


class PlanDefinitionActionPrecheckBehavior(models.TextChoices):
    """PlanDefinition action precheck behavior choices."""

    YES = "yes", _("Yes")
    NO = "no", _("No")


class PlanDefinitionActionCardinalityBehavior(models.TextChoices):
    """PlanDefinition action cardinality behavior choices."""

    SINGLE = "single", _("Single")
    MULTIPLE = "multiple", _("Multiple")


class PlanDefinitionActionParticipantType(models.TextChoices):
    """PlanDefinition action participant type choices."""

    CARE_TEAM = "care-team", _("Care Team")
    DEVICE = "device", _("Device")
    GROUP = "group", _("Group")
    HEALTHCARE_SERVICE = "healthcareservice", _("Healthcare Service")
    LOCATION = "location", _("Location")
    ORGANIZATION = "organization", _("Organization")
    PATIENT = "patient", _("Patient")
    PRACTITIONER = "practitioner", _("Practitioner")
    PRACTITIONER_ROLE = "practitionerrole", _("Practitioner Role")
    RELATED_PERSON = "relatedperson", _("Related Person")


class PlanDefinitionActionRelatedActionRelationship(models.TextChoices):
    """PlanDefinition action related action relationship choices."""

    BEFORE_START = "before-start", _("Before Start")
    BEFORE = "before", _("Before")
    BEFORE_END = "before-end", _("Before End")
    CONCURRENT_WITH_START = "concurrent-with-start", _("Concurrent with Start")
    CONCURRENT = "concurrent", _("Concurrent")
    CONCURRENT_WITH_END = "concurrent-with-end", _("Concurrent with End")
    AFTER_START = "after-start", _("After Start")
    AFTER = "after", _("After")
    AFTER_END = "after-end", _("After End")


class PlanDefinitionActionConditionKind(models.TextChoices):
    """PlanDefinition action condition kind choices."""

    APPLICABILITY = "applicability", _("Applicability")
    START = "start", _("Start")
    STOP = "stop", _("Stop")
