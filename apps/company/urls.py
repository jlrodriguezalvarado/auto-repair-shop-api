from django.urls import path
from apps.company.views.api import MyCompanyView

app_name = "company"

urlpatterns = [
    path("", MyCompanyView.as_view(), name="company-detail"),
]
