from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone


class Sport(models.Model):
    """A sport such as Cricket or Football (used for the sport filter)."""
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=8, blank=True, help_text='Optional emoji shown on the site')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """A type of equipment such as Balls, Footwear or Apparel."""
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    @property
    def in_stock(self):
        return self.is_available and self.stock > 0


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Order Placed'),
        ('confirmed', 'Confirmed'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    # The normal journey of an order (cancelled is a separate ending)
    STEP_ORDER = ['pending', 'confirmed', 'dispatched', 'delivered']

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    address = models.TextField()
    city = models.CharField(max_length=60)
    pincode = models.CharField(max_length=6)
    payment_method = models.CharField(max_length=30, default='Cash on Delivery', editable=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    # Date and time when each stage was reached (filled automatically)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} by {self.user}'

    def _old_status(self):
        if not self.pk:
            return None
        return Order.objects.filter(pk=self.pk).values_list('status', flat=True).first()

    def clean(self):
        old = self._old_status()
        if old == 'cancelled' and self.status != 'cancelled':
            raise ValidationError('A cancelled order cannot be reopened.')
        if old == 'delivered' and self.status == 'cancelled':
            raise ValidationError('A delivered order cannot be cancelled.')

    def save(self, *args, **kwargs):
        old_status = self._old_status()

        # Record the time when the order reaches a new stage
        stamp_field = {'confirmed': 'confirmed_at', 'dispatched': 'dispatched_at',
                       'delivered': 'delivered_at', 'cancelled': 'cancelled_at'}.get(self.status)
        if stamp_field and getattr(self, stamp_field) is None:
            setattr(self, stamp_field, timezone.now())

        super().save(*args, **kwargs)

        # A cancelled order puts its items back into stock (only once)
        if self.status == 'cancelled' and old_status not in (None, 'cancelled'):
            for item in self.items.all():
                Product.objects.filter(pk=item.product_id).update(stock=F('stock') + item.quantity)

    @property
    def can_cancel(self):
        return self.status in ('pending', 'confirmed')

    @property
    def tracking_steps(self):
        """The four delivery stages with their dates, used by the tracking bar."""
        stages = [('pending', 'Order Placed', self.created_at),
                  ('confirmed', 'Confirmed', self.confirmed_at),
                  ('dispatched', 'Dispatched', self.dispatched_at),
                  ('delivered', 'Delivered', self.delivered_at)]
        current = self.STEP_ORDER.index(self.status) if self.status in self.STEP_ORDER else 0
        return [{'label': label, 'date': date, 'done': index <= current}
                for index, (key, label, date) in enumerate(stages)]

    def items_summary(self):
        text = ', '.join(f'{item.product.name} x{item.quantity}' for item in self.items.all())
        return text if len(text) <= 70 else text[:67] + '...'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)  # price at the time of purchase

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    @property
    def subtotal(self):
        return self.price * self.quantity
