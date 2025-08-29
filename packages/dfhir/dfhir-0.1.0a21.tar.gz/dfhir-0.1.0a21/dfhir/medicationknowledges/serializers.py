"""medication knowledge serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    ContactDetailSerializer,
    DurationSerializer,
    IdentifierSerializer,
    MoneySerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    RatioSerializer,
    SimpleQuantitySerializer,
)
from dfhir.documentreferences.serializers import DocumentReferenceReferenceSerializer
from dfhir.medicationknowledges.models import (
    MedicationKnowledge,
    MedicationKnowledgeCost,
    MedicationKnowledgeDefinitional,
    MedicationKnowledgeDefinitionalDrugCharacteristic,
    MedicationKnowledgeDefinitionalIngredient,
    MedicationKnowledgeIndicationGuideline,
    MedicationKnowledgeIndicationGuidelineDosingGuideline,
    MedicationKnowledgeIndicationGuidelineDosingGuidelineDosage,
    MedicationKnowledgeMedicineClassification,
    MedicationKnowledgeMonitoringProgram,
    MedicationKnowledgeMonograph,
    MedicationKnowledgePackaging,
    MedicationKnowledgePatientCharacteristics,
    MedicationKnowledgeReference,
    MedicationKnowledgeRegulatory,
    MedicationKnowledgeRegulatoryMaxDispense,
    MedicationKnowledgeRegulatorySubstitution,
    MedicationKnowledgeRelatedMedicationKnowledge,
    MedicationKnowledgeStorageGuideline,
    MedicationKnowledgeStorageGuidelineEnvironmentalSetting,
)
from dfhir.medications.serializers import MedicationReferenceSerializer
from dfhir.substances.serializers import SubstanceCodeableReferenceSerializer


class MedicationKnowledgeReferenceSerializer(BaseReferenceModelSerializer):
    """Medication knowledge reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = MedicationKnowledgeReference
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeRelatedMedicationKnowledgeSerializer(
    WritableNestedModelSerializer
):
    """medication knowledge related medication knowledge serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    reference = MedicationKnowledgeReferenceSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgeRelatedMedicationKnowledge
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeMonographSerializer(WritableNestedModelSerializer):
    """Medication knowledge monograph serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    source = DocumentReferenceReferenceSerializer(required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgeMonograph
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeCostSerializer(WritableNestedModelSerializer):
    """Medication knowledge cost serializer."""

    effective_date = PeriodSerializer(required=False, many=True)
    type = CodeableConceptSerializer(many=False, required=False)
    source = DocumentReferenceReferenceSerializer(required=False)
    cost_money = MoneySerializer(required=False)
    cost_codeable_concept = CodeableConceptSerializer(required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgeCost
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeMonitoringProgramSerializer(WritableNestedModelSerializer):
    """Medication knowledge monitoring program serializer."""

    type = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgeMonitoringProgram
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgePatientCharacteristicsSerializer(
    WritableNestedModelSerializer
):
    """Medication knowledge dosing guideline treatment intent dosage patient characteristics serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    value_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    value_quantity = MoneySerializer(many=False, required=False)
    value_range = MoneySerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgePatientCharacteristics
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeIndicationGuidelineDosingGuidelineDosageSerializer(
    WritableNestedModelSerializer
):
    """Medication knowledge dosing guideline dosage serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    # TODO: dose = DoseSerializer(many=False, required=False)
    administration_treatment = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgeIndicationGuidelineDosingGuidelineDosage
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeIndicationGuidelineDosingGuidelineSerializer(
    WritableNestedModelSerializer
):
    """Medication knowledge indication guideline dosing guideline serializer."""

    treatment_intent = CodeableConceptSerializer(many=False, required=False)
    dosage = MedicationKnowledgeIndicationGuidelineDosingGuidelineDosageSerializer(
        many=True, required=False
    )
    administration_treatment = CodeableConceptSerializer(many=False, required=False)
    patient_characteristics = MedicationKnowledgePatientCharacteristicsSerializer(
        many=True, required=False
    )

    class Meta:
        """meta options."""

        model = MedicationKnowledgeIndicationGuidelineDosingGuideline
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeIndicationGuidelineSerializer(WritableNestedModelSerializer):
    """Medication knowledge indication guideline serializer."""

    dosing_guideline = MedicationKnowledgeIndicationGuidelineDosingGuidelineSerializer(
        many=True, required=False
    )

    class Meta:
        """meta options."""

        model = MedicationKnowledgeIndicationGuideline
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeMedicineClassificationSerializer(
    WritableNestedModelSerializer
):
    """Medication knowledge medicine classification serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    classification = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgeMedicineClassification
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgePackagingSerializer(WritableNestedModelSerializer):
    """Medication knowledge packaging serializer."""

    cost = MedicationKnowledgeCostSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgePackaging
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeStorageGuidelineEnvironmentalSettingSerializer(
    WritableNestedModelSerializer
):
    """Medication knowledge storage guideline environmental setting serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    value_quantity = MoneySerializer(many=False, required=False)
    value_range = MoneySerializer(many=False, required=False)
    value_codeable_concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgeStorageGuidelineEnvironmentalSetting
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeStorageGuidelineSerializer(WritableNestedModelSerializer):
    """Medication knowledge storage guideline serializer."""

    note = AnnotationSerializer(many=True, required=False)
    stability_duration = DurationSerializer(required=False)
    environmental_setting = (
        MedicationKnowledgeStorageGuidelineEnvironmentalSettingSerializer(
            many=True, required=False
        )
    )

    class Meta:
        """meta options."""

        model = MedicationKnowledgeStorageGuideline
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeRegulatorySubstitutionSerializer(
    WritableNestedModelSerializer
):
    """Medication knowledge regulatory substitution serializer."""

    type = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgeRegulatorySubstitution
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeRegulatoryMaxDispenseSerializer(WritableNestedModelSerializer):
    """Medication knowledge regulatory max dispense serializer."""

    quantity = SimpleQuantitySerializer(required=False)
    period = PeriodSerializer(required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgeRegulatoryMaxDispense
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeRegulatorySerializer(WritableNestedModelSerializer):
    """Medication knowledge regulatory serializer."""

    regulatory_authority = OrganizationReferenceSerializer(many=False, required=False)
    substitution = MedicationKnowledgeRegulatorySubstitutionSerializer(
        many=True, required=False
    )
    schedule = CodeableConceptSerializer(many=False, required=False)
    max_dispense = MedicationKnowledgeRegulatoryMaxDispenseSerializer(
        many=True, required=False
    )

    class Meta:
        """meta options."""

        model = MedicationKnowledgeRegulatory
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeDefinitionalIngredientSerializer(
    WritableNestedModelSerializer
):
    """Medication knowledge definitional ingredient serializer."""

    item = SubstanceCodeableReferenceSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    strength_ratio = RatioSerializer(many=False, required=False)
    strength_quantity = SimpleQuantitySerializer(many=False, required=False)
    strength_codeable_concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgeDefinitionalIngredient
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeDefinitionalDrugCharacteristicSerializer(
    WritableNestedModelSerializer
):
    """medication knowledge definitional ingredient serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    value_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    value_quantity = MoneySerializer(many=False, required=False)
    value_attachment = AttachmentSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationKnowledgeDefinitionalDrugCharacteristic
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeDefinitionalSerializer(WritableNestedModelSerializer):
    """medication knowledge definitional serializer."""

    dose_form = CodeableConceptSerializer(many=False, required=False)
    intended_route = CodeableConceptSerializer(many=False, required=False)
    ingredient = MedicationKnowledgeDefinitionalIngredientSerializer(
        required=False, many=True
    )
    drug_characteristic = MedicationKnowledgeDefinitionalDrugCharacteristicSerializer(
        many=True, required=False
    )

    class Meta:
        """meta options."""

        model = MedicationKnowledgeDefinitional
        exclude = ["created_at", "updated_at"]


class MedicationKnowledgeSerializer(BaseWritableNestedModelSerializer):
    """Medication knowledge serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    code = CodeableConceptSerializer(many=False, required=False)
    author = ContactDetailSerializer(many=False, required=False)
    jurisdiction = CodeableConceptSerializer(many=True, required=False)
    related_medication_knowledge = (
        MedicationKnowledgeRelatedMedicationKnowledgeSerializer(
            many=True, required=False
        )
    )
    associate_medication = MedicationReferenceSerializer(many=True, required=False)
    product_type = CodeableConceptSerializer(many=True, required=False)
    monograph = MedicationKnowledgeMonographSerializer(many=True, required=False)
    cost = MedicationKnowledgeCostSerializer(many=True, required=False)
    monitoring_program = MedicationKnowledgeMonitoringProgramSerializer(
        many=True, required=False
    )
    indication_guideline = MedicationKnowledgeIndicationGuidelineSerializer(
        many=True, required=False
    )
    medicine_classification = MedicationKnowledgeMedicineClassificationSerializer(
        many=True, required=False
    )
    packaging = MedicationKnowledgePackagingSerializer(many=True, required=False)
    storage_guideline = MedicationKnowledgeStorageGuidelineSerializer(
        many=True, required=False
    )
    regulatory = MedicationKnowledgeRegulatorySerializer(many=True, required=False)
    definitional = MedicationKnowledgeDefinitionalSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = MedicationKnowledge
        exclude = ["created_at", "updated_at"]
