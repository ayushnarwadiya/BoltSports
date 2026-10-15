from decimal import Decimal

from .models import Product

CART_SESSION_KEY = 'cart'


class Cart:
    """A shopping cart stored in the user's session: {product_id: quantity}."""

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(CART_SESSION_KEY, {})

    def _save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True

    def add(self, product, quantity=1):
        key = str(product.id)
        new_quantity = self.cart.get(key, 0) + quantity
        self.cart[key] = min(new_quantity, product.stock)  # never more than the stock
        self._save()

    def set_quantity(self, product, quantity):
        if quantity <= 0:
            self.remove(product)
            return
        self.cart[str(product.id)] = min(quantity, product.stock)
        self._save()

    def remove(self, product):
        self.cart.pop(str(product.id), None)
        self._save()

    def clear(self):
        self.cart = {}
        self._save()

    def __iter__(self):
        products = Product.objects.filter(id__in=self.cart.keys()).select_related('sport')
        for product in products:
            quantity = self.cart[str(product.id)]
            yield {
                'product': product,
                'quantity': quantity,
                'subtotal': product.price * quantity,
            }

    def __len__(self):
        """Total number of items in the cart."""
        return sum(self.cart.values())

    def get_total(self):
        return sum((item['subtotal'] for item in self), Decimal('0'))
