from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from api.models import TickerAggregate


@receiver(post_save, sender=TickerAggregate)
def broadcast_trade_update(sender, instance, **kwargs):

    channel_layer = get_channel_layer()
    data = {
        "symbol": instance.symbol,
        "open_price": str(instance.open_price),
        "close_price": str(instance.close_price),
        "high_price": str(instance.high_price),
        "low_price": str(instance.low_price),
        "volume": str(instance.volume),
    }
    async_to_sync(channel_layer.group_send)(
        "trades", {"type": "send_trade_update", "data": data}
    )  # send the message to the group
