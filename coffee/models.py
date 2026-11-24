from decimal import Decimal
from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    class Roast(models.TextChoices):
        LIGHT = 'light', 'Светлая'
        MEDIUM = 'medium', 'Средняя'
        DARK = 'dark', 'Тёмная'

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2)
    weight_grams = models.PositiveIntegerField('Вес, г', default=250)
    roast = models.CharField('Обжарка', max_length=10, choices=Roast.choices, default=Roast.MEDIUM)
    stock = models.PositiveIntegerField('Остаток', default=0)
    is_available = models.BooleanField('Доступен', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        PAID = 'paid', 'Оплачен'
        SHIPPED = 'shipped', 'Отправлен'
        DONE = 'done', 'Выполнен'
        CANCELED = 'canceled', 'Отменён'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    address = models.CharField('Адрес доставки', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    @property
    def total(self):
        return sum((i.price * i.quantity for i in self.items.all()), Decimal('0'))

    def __str__(self):
        return f'Заказ #{self.pk}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField('Цена за единицу', max_digits=8, decimal_places=2)

    class Meta:
        ordering = ['id']