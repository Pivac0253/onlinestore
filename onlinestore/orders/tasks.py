from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Order
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def order_created(self, order_id):
    """
    Задача для отправки уведомления по электронной почте при успешном создании заказа.
    """
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Order nr. {order.id}'

        html_message = render_to_string('orders/order_email.html', {'order': order})
        plain_message = strip_tags(html_message)

        mail_sent = send_mail(
            subject,
            plain_message,
            'admin@myshop.com',
            [order.email],
            html_message=html_message,
            fail_silently=False
        )

        if not mail_sent:
            raise Exception("Email не был отправлен")

        return mail_sent

    except Exception as e:
        logger.error(f"Ошибка при отправке email для заказа {order_id}: {str(e)}")
        if settings.DEBUG:
            # В режиме разработки просто выводим ошибку
            print(f"Ошибка отправки email: {e}")
            raise
        else:
            # В production пробуем повторить через 5 минут
            raise self.retry(exc=e, countdown=300)

