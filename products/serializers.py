from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Products with brand and stock info."""
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'sku', 
            'purchase_price', 'selling_price', 'mrp', 
            'stock_quantity', 'min_stock_level', 'image',
            'is_low_stock', 'is_active', 'created_at'
        ]
