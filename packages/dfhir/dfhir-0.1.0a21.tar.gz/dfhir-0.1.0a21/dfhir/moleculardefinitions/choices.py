"""molecular definition model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class MolecularDefinitionStatusChoices(TextChoices):
    """molecular definition status choices."""

    AA = "aa", _("aa")
    DNA = "dna", _("dna")
    MA = "ma", _("ma")
