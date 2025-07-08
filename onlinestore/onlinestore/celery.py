import os
from celery import Celery

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')

app = Celery('myshop')

# Использование строки здесь означает, что работник не должен сериализовать
# конфигурационный объект дочерним процессам.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Загрузка задач из всех зарегистрированных приложений Django
app.autodiscover_tasks()