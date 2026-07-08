from django.contrib import admin
from .models import Estimate, EstimateService, EstimateItem

@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    pass

@admin.register(EstimateService)
class EstimateServiceAdmin(admin.ModelAdmin):
    pass

@admin.register(EstimateItem)
class EstimateItemAdmin(admin.ModelAdmin):
    pass
