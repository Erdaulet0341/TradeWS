from django.urls import path

from api.consumers import TradeConsumer

websocket_urlpatterns = [
    path('ws/trade/', TradeConsumer.as_asgi()),
]
