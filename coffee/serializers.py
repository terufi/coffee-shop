from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from .models import Category, Product, Order, OrderItem


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'weight_grams', 'roast','stock', 'is_available', 'category', 'category_name', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']
        read_only_fields = ['price']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    items = OrderItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'address', 'items', 'total', 'created_at']
        read_only_fields = ['status']

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('Заказ не может быть пустым.')
        return items

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item in items_data:
            product = item['product']
            qty = item['quantity']
            if not product.is_available or product.stock < qty:
                raise serializers.ValidationError(
                    f'Товара «{product.name}» недостаточно на складе.')
            product.stock -= qty
            product.save(update_fields=['stock'])
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=product.price)
        return order

    def update(self, instance, validated_data):
        validated_data.pop('items', None)  # состав заказа после создания не меняем
        return super().update(instance, validated_data)