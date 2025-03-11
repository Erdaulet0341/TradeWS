import asyncio
import json
import websockets
import redis
from django.core.management.base import BaseCommand

from TradeWS.variables import REDIS_HOST, REDIS_PORT, BINANCE_WS_URL, TIME_INTERVAL, SYMBOLS


class Command(BaseCommand):
    help = "Listen to Binance WebSocket and save trades to Redis"

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.listen_binance())  # run the async function

    async def listen_binance(self):
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

        while True:
            try:
                async with websockets.connect(BINANCE_WS_URL) as websocket:
                    subscribe_message = {
                        "method": "SUBSCRIBE",
                        "params": [f"{symbol}@trade" for symbol in SYMBOLS],
                        "id": 1
                    }
                    await websocket.send(json.dumps(subscribe_message))

                    async for message in websocket:
                        data = json.loads(message)
                        if "s" in data and "p" in data:
                            symbol = data["s"].lower()
                            trade_data = {
                                "symbol": symbol,
                                "price": data["p"],
                                "quantity": data["q"],
                                "trade_time": data["T"],
                            }
                            r.lpush(f"trades:{symbol}", json.dumps(trade_data)) # save trade to Redis
                            r.ltrim(f"trades:{symbol}", 0, TIME_INTERVAL)
            except Exception as e:
                self.stderr.write(f"Error: {e}, reconnecting...")
                await asyncio.sleep(5) # reconnect after 5 seconds
