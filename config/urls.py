from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # API
    path("api/users/", include("apps.users.urls", namespace="users")),
    path("api/company/", include("apps.company.urls", namespace="company")),
    path("api/customers/", include("apps.customers.urls", namespace="customers")),
    path("api/vehicles/", include("apps.vehicles.urls", namespace="vehicles")),
    path("api/catalog/", include("apps.catalog.urls", namespace="catalog")),
    path("api/work-orders/", include("apps.work_orders.urls", namespace="work_orders")),
    path("api/estimates/", include("apps.estimates.urls", namespace="estimates")),
    path("api/receipts/", include("apps.receipts.urls", namespace="receipts")),
    path("api/dashboard/", include("apps.dashboard.urls", namespace="dashboard")),

    # Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
