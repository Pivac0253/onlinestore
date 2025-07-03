from .cart import Cart
from django.core.exceptions import ImproperlyConfigured

def cart(request):
    try:
        if hasattr(request, 'session'):
            return {'cart': Cart(request)}
        return {'cart': None}
    except (KeyError, ImproperlyConfigured):
        return {'cart': None}