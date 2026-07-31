from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_id", "email", "phone")
    search_fields = ("name", "tax_id", "email")
