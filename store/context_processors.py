from .cart import Cart


def cart(request):
    """Makes the cart item count available in every template."""
    return {'cart_count': len(Cart(request))}
