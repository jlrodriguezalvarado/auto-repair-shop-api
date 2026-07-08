from django.urls import path
from apps.company.views.api import CompanyView

app_name = "company"

urlpatterns = [
    path("", CompanyView.as_view(), name="company-detail"),
]
