from rest_framework import serializers
from .models import User, Order, Product, ProductAnalytics


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'username', 'product_id', 'product_name', 
                  'quantity', 'total_price', 'status', 'order_date']
        read_only_fields = ['id', 'order_date', 'total_price', 'product_name']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 
                  'category', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductAnalyticsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', 
                                              max_digits=10, decimal_places=2, 
                                              read_only=True)
    
    class Meta:
        model = ProductAnalytics
        fields = ['id', 'product', 'product_name', 'product_price', 
                  'total_sold', 'revenue_generated', 'last_updated']
        read_only_fields = ['id', 'last_updated']
