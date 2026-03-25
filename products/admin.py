from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'brand', 'selling_price', 
        'stock_quantity', 'is_low_stock_status', 'is_active'
    )
    list_filter = ('brand', 'is_active')
    search_fields = ('name', 'brand', 'sku')
    ordering = ('-created_at',)
    
    # Read-only fields in form
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    # Custom colored indicator for low stock
    @admin.display(description="Stock Status")
    def is_low_stock_status(self, obj):
        if obj.is_low_stock:
            return "⚠️ Low Stock"
        return "✅ In Stock"
