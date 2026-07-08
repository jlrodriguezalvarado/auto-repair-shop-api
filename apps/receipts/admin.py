from django.contrib import admin
from .models import Receipt, ReceiptService, ReceiptItem, ReceiptPayment

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    pass

@admin.register(ReceiptService)
class ReceiptServiceAdmin(admin.ModelAdmin):
    pass

@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    pass

@admin.register(ReceiptPayment)
class ReceiptPaymentAdmin(admin.ModelAdmin):
    pass
