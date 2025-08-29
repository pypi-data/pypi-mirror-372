"""service requests urls."""

from django.urls import path

from . import views

app_name = "servicerequests"

urlpatterns = [
    path("servicerequests/", views.ServiceRequestListView.as_view(), name="list_view"),
    path(
        "servicerequests/<int:pk>/",
        views.ServiceRequestDetailView.as_view(),
        name="detail_view",
    ),
    path("servicerequests/reason/", views.ProcedureReasonListView.as_view()),
    path("servicerequests/bodysite/", views.BodySiteListView.as_view()),
    path("servicerequests/code/", views.ProcedureCodesListView.as_view()),
    path("servicerequests/asneeded/", views.AsNeededListView.as_view()),
    path("servicerequests/category/", views.ServiceRequestCategoryListView.as_view()),
    path("servicerequests/reference/", views.ReferenceListView.as_view()),
    path("servicerequests/parameter/", views.ParameterListView.as_view()),
]
