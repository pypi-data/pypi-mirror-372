"""medication requests urls."""

from django.urls import path

from dfhir.medicationrequests.views import (
    AdditionalIllustrationList,
    DosageMethodList,
    DosageRouteList,
    DosageSiteList,
    MediationRequestReferenceTypeList,
    MedicationRequestCategoryList,
    MedicationRequestDetail,
    MedicationRequestList,
    MedicationRequestMedicationCodeList,
    MedicationRequestReasonList,
    ReferenceAsNeededForList,
)

app_name = "medicationrequests"

urlpatterns = [
    path(
        "medicationrequests/",
        MedicationRequestList.as_view(),
        name="medicationrequest-list",
    ),
    path(
        "medicationrequests/<int:pk>/",
        MedicationRequestDetail.as_view(),
        name="medicationrequest-detail",
    ),
    path(
        "medicationrequests/reference-type/",
        MediationRequestReferenceTypeList.as_view(),
        name="medicationrequest-reference-type-list",
    ),
    path(
        "medicationrequests/category/",
        MedicationRequestCategoryList.as_view(),
        name="medicationrequest-category-list",
    ),
    path(
        "medicationrequests/reason/",
        MedicationRequestReasonList.as_view(),
        name="medicationrequest-reason-list",
    ),
    path(
        "medicationrequests/medication-code/",
        MedicationRequestMedicationCodeList.as_view(),
        name="medicationrequest-medication-code-list",
    ),
    path(
        "medicationrequests/dosage-method/",
        DosageMethodList.as_view(),
        name="medicationrequest-dosage-method-list",
    ),
    path(
        "medicationrequests/dosage-route/",
        DosageRouteList.as_view(),
        name="medicationrequest-dosage-route-list",
    ),
    path(
        "medicationrequests/dosage-site/",
        DosageSiteList.as_view(),
        name="medicationrequest-dosage-site-list",
    ),
    path(
        "medicationrequests/additional-illustration/",
        AdditionalIllustrationList.as_view(),
        name="medicationrequest-additional-illustration-list",
    ),
    path(
        "medicationrequests/as-needed-for/",
        ReferenceAsNeededForList.as_view(),
        name="medicationrequest-as-needed-for-list",
    ),
]
