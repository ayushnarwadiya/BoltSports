from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Category, Order, OrderItem, Product, Sport


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'category', 'price', 'stock', 'is_available')
    list_filter = ('sport', 'category', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_available')
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price', 'subtotal')
    readonly_fields = ('product', 'quantity', 'price', 'subtotal')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # The list shows WHO ordered, WHAT they ordered and the delivery status
    list_display = ('id', 'customer', 'phone', 'city', 'items_summary', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'city')
    search_fields = ('id', 'full_name', 'phone', 'user__username', 'user__email')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    actions = ['mark_confirmed', 'mark_dispatched', 'mark_delivered', 'mark_cancelled']

    readonly_fields = ('user', 'customer_email', 'total', 'payment_method', 'created_at',
                       'confirmed_at', 'dispatched_at', 'delivered_at', 'cancelled_at')
    fieldsets = (
        ('Customer', {'fields': ('user', 'customer_email', 'full_name', 'phone')}),
        ('Delivery address', {'fields': ('address', 'city', 'pincode')}),
        ('Order details', {'fields': ('total', 'payment_method', 'created_at')}),
        ('Delivery status', {'fields': ('status', 'confirmed_at', 'dispatched_at',
                                        'delivered_at', 'cancelled_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('items__product')

    @admin.display(description='Customer', ordering='user__username')
    def customer(self, order):
        return f'{order.full_name} ({order.user.username})'

    @admin.display(description='Items')
    def items_summary(self, order):
        return order.items_summary()

    @admin.display(description='Email')
    def customer_email(self, order):
        return order.user.email or '-'

    # ---- actions to change the delivery status of many orders at once ----
    def _change_status(self, request, queryset, status, label):
        done = 0
        for order in queryset:
            order.status = status
            try:
                order.clean()
            except ValidationError as error:
                self.message_user(request, f'Order #{order.id}: {error.messages[0]}', messages.WARNING)
                continue
            order.save()
            done += 1
        self.message_user(request, f'{done} order(s) marked as {label}.')

    @admin.action(description='Mark selected orders as Confirmed')
    def mark_confirmed(self, request, queryset):
        self._change_status(request, queryset, 'confirmed', 'Confirmed')

    @admin.action(description='Mark selected orders as Dispatched')
    def mark_dispatched(self, request, queryset):
        self._change_status(request, queryset, 'dispatched', 'Dispatched')

    @admin.action(description='Mark selected orders as Delivered')
    def mark_delivered(self, request, queryset):
        self._change_status(request, queryset, 'delivered', 'Delivered')

    @admin.action(description='Cancel selected orders (stock is returned)')
    def mark_cancelled(self, request, queryset):
        self._change_status(request, queryset, 'cancelled', 'Cancelled')
