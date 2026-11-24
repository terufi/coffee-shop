from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, generics, permissions, filters
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Category, Product, Order
from .serializers import (CategorySerializer, ProductSerializer,OrderSerializer, RegisterSerializer)
from .permissions import IsAdminOrReadOnly


def crud_docs(tag, one, many):
    """Русские названия раздела и описания для 6 стандартных действий CRUD."""
    return extend_schema_view(
        list=extend_schema(tags=[tag], summary=f'Список: {many}'),
        create=extend_schema(tags=[tag], summary=f'Создать: {one}'),
        retrieve=extend_schema(tags=[tag], summary=f'Получить по id: {one}'),
        update=extend_schema(tags=[tag], summary=f'Полностью обновить: {one}'),
        partial_update=extend_schema(tags=[tag], summary=f'Частично обновить: {one}'),
        destroy=extend_schema(tags=[tag], summary=f'Удалить: {one}'),
    )


# ---------- Аутентификация ----------

@extend_schema(tags=['Аутентификация'], summary='Регистрация пользователя')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=['Аутентификация'],summary='Получить JWT-токен (логин и пароль)')
class TokenView(TokenObtainPairView):
    pass


@extend_schema(tags=['Аутентификация'],summary='Обновить access-токен по refresh-токену')
class TokenRefresh(TokenRefreshView):
    pass


# ---------- Каталог ----------

@crud_docs('Категории', 'категория', 'категории')
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


@crud_docs('Товары', 'товар', 'товары')
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'created_at']


# ---------- Заказы ----------

@crud_docs('Заказы', 'заказ', 'заказы')
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # для генерации Swagger
            return Order.objects.none()
        qs = Order.objects.select_related('user').prefetch_related('items__product')
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)  # покупатель видит только свои заказы

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)