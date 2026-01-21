from django.contrib import admin
from .models import Category, Supplier, JewelryItem, StockTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'created_at']
    search_fields = ['name', 'contact_person', 'email']
    list_filter = ['created_at']
    ordering = ['name']


@admin.register(JewelryItem)
class JewelryItemAdmin(admin.ModelAdmin):
    list_display = [
        'sku', 'name', 'category', 'selling_price', 
        'quantity', 'metal_type', 'is_active', 'created_at'
    ]
    list_filter = ['category', 'metal_type', 'is_active', 'supplier']
    search_fields = ['sku', 'name', 'description', 'gemstone']
    list_editable = ['quantity', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('sku', 'name', 'description', 'category', 'supplier', 'image')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price', 'quantity')
        }),
        ('Details', {
            'fields': ('weight_grams', 'metal_type', 'gemstone')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['item', 'transaction_type', 'quantity', 'user', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['item__name', 'item__sku', 'notes']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    ordering = ['-created_at']
