"""diagnosticreports URL Configuration."""

from django.urls import path

from . import views

app_name = "diagnosticreports"

urlpatterns = [
    path(
        "diagnosticreports/", views.DiagnosticReportListView.as_view(), name="list_view"
    ),
    path(
        "diagnosticreports/<int:pk>/",
        views.DiagnosticReportDetailView.as_view(),
        name="detail_view",
    ),
    path(
        "diagnosticreports/codes/",
        views.DiagnosticReportCodeListView.as_view(),
        name="codes_list_view",
    ),
    path(
        "diagnosticreports/categories/",
        views.DiagnosticCategoryListView.as_view(),
        name="categories_list_view",
    ),
    path(
        "diagnosticreports/conclusioncodes/",
        views.ConclusionCodeListView.as_view(),
        name="conclusion_list_view",
    ),
]
