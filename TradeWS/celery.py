from celery import Celery

from TradeWS.variables import CELERY_BROKER_URL

app = Celery(
    'TradeWS',
    broker=CELERY_BROKER_URL,
    include=['TradeWS.tasks',]
)

app.conf.timezone = 'Asia/Almaty'  # UTC+5
app.conf.enable_utc = True

app.config_from_object('django.conf:settings', namespace='CELERY')
