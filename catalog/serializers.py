from rest_framework import serializers
from decimal import Decimal

class ProductSerializer(serializers.Serializer):
    """
    Serializer pour les produits du catalogue Supabase.
    Approche débutant avec validation simple.
    """
    
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = serializers.CharField(max_length=100)
    image_url = serializers.URLField(required=False, allow_blank=True)
    stock_quantity = serializers.IntegerField(min_value=0)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_price(self, value):
        """Validation du prix (doit être positif)."""
        if value <= Decimal('0'):
            raise serializers.ValidationError("Le prix doit être supérieur à 0.")
        return value

class ProductListSerializer(serializers.Serializer):
    """
    Serializer simplifié pour la liste des produits (performances).
    """
    
    id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = serializers.CharField()
    image_url = serializers.URLField(required=False)
    stock_quantity = serializers.IntegerField()
    is_active = serializers.BooleanField()