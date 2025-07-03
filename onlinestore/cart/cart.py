from decimal import Decimal
from django.conf import settings
from django.apps import apps


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)  # Сохраняем как строку
            }

        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        # Убедимся, что все Decimal преобразованы в строки
        for item in self.cart.values():
            if isinstance(item.get('price'), Decimal):
                item['price'] = str(item['price'])
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        Product = apps.get_model('shop', 'Product')
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            try:
                # Преобразуем строку обратно в Decimal для расчетов
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
            except (TypeError, ValueError, InvalidOperation):
                # Обработка ошибок преобразования
                item['price'] = Decimal('0')
                item['total_price'] = Decimal('0')
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        total = Decimal('0')
        for item in self.cart.values():
            try:
                # Безопасное преобразование и расчет
                price = Decimal(item['price'])
                total += price * item['quantity']
            except (TypeError, ValueError, InvalidOperation):
                continue
        return total

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.session.modified = True


