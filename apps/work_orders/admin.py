from django.contrib import admin
from .models import WorkOrder, WorkOrderService, WorkOrderItem

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    pass

@admin.register(WorkOrderService)
class WorkOrderServiceAdmin(admin.ModelAdmin):
    pass

@admin.register(WorkOrderItem)
class WorkOrderItemAdmin(admin.ModelAdmin):
    pass
