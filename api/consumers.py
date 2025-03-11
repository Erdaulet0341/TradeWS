# api/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from api.models import TickerAggregate


class TradeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("trades", self.channel_name)  # add the consumer to the group
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("trades", self.channel_name)  # remove the consumer from the group

    async def receive(self, text_data):
        data = json.loads(text_data)
        symbol = data.get("symbol")

        ticker = await sync_to_async(TickerAggregate.objects.filter(symbol=symbol).latest)("id")
        await self.send(text_data=json.dumps({
            "symbol": ticker.symbol,
            "open_price": str(ticker.open_price),
            "close_price": str(ticker.close_price),
            "high_price": str(ticker.high_price),
            "low_price": str(ticker.low_price),
            "volume": str(ticker.volume),
        }))  # send the latest ticker data

    async def send_trade_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
