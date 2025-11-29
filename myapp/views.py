from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import User, Order, Product, ProductAnalytics
from .serializers import (
    UserSerializer, OrderSerializer, 
    ProductSerializer, ProductAnalyticsSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.using('default').all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        user = self.get_object()
        orders = Order.objects.using('default').filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.using('products_db').all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        try:
            product = self.get_object()
            analytics = ProductAnalytics.objects.using('products_db').get(product=product)
            serializer = ProductAnalyticsSerializer(analytics)
            return Response(serializer.data)
        except ProductAnalytics.DoesNotExist:
            return Response(
                {'error': 'Analytics not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        products = Product.objects.using('products_db').filter(stock__lt=10)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.using('default').all()
    serializer_class = OrderSerializer

    def create(self, request):
        user_id = request.data.get('user')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not all([user_id, product_id, quantity]):
            return Response(
                {'error': 'user, product_id, and quantity are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.using('default').get(id=user_id)
            product = Product.objects.using('products_db').get(id=product_id)
            
            if product.stock < int(quantity):
                return Response(
                    {'error': f'Insufficient stock. Available: {product.stock}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            total_price = product.price * int(quantity)

            with transaction.atomic(using='default'):
                order = Order.objects.using('default').create(
                    user=user,
                    product_id=product_id,
                    product_name=product.name,
                    quantity=quantity,
                    total_price=total_price,
                    status='completed'
                )

            with transaction.atomic(using='products_db'):
                product.stock -= int(quantity)
                product.save(using='products_db')

                analytics, created = ProductAnalytics.objects.using('products_db').get_or_create(
                    product=product,
                    defaults={'total_sold': 0, 'revenue_generated': 0}
                )
                analytics.total_sold += int(quantity)
                analytics.revenue_generated += total_price
                analytics.save(using='products_db')

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def recent_orders(self, request):
        orders = Order.objects.using('default').all()[:10]
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
