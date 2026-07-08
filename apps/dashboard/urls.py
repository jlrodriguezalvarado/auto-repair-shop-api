from django.urls import path
from apps.dashboard.views.api import DashboardSummaryView

app_name = "dashboard"

urlpatterns = [
    path("summary/", DashboardSummaryView.as_view(), name="summary"),
]
