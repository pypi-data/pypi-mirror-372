"""molecular sequences model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class MolecularSequenceTypeChoices(TextChoices):
    """Molecular sequence type choices."""

    AA = "aa", _("Amino acid")
    DNA = "dna", _("DNA")
    RNA = "rna", _("RNA")
