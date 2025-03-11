import json
from datetime import datetime

import redis
from django.utils import timezone

from TradeWS.celery import app
from TradeWS.variables import REDIS_HOST, REDIS_PORT, SYMBOLS
from api.models import Trade, TickerAggregate


@app.task
def aggregate_trades():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    for symbol in SYMBOLS:
        trades_key = f"trades:{symbol}"
        trades = r.lrange(trades_key, 0, -1)

        if trades:
            trade_data = [json.loads(trade) for trade in trades]
            prices = [float(trade["price"]) for trade in trade_data]
            quantities = [float(trade["quantity"]) for trade in trade_data]
            trade_times = [datetime.fromtimestamp(int(trade["trade_time"]) / 1000) for trade in trade_data]

            start_time = min(trade_times)
            end_time = max(trade_times)
            open_price = prices[0]
            close_price = prices[-1]
            high_price = max(prices)
            low_price = min(prices)
            volume = sum(quantities)

            TickerAggregate.objects.create(
                symbol=symbol.upper(),
                start_time=start_time,
                end_time=end_time,
                open_price=open_price,
                close_price=close_price,
                high_price=high_price,
                low_price=low_price,
                volume=volume
            )  # save the aggregated data to the database

            avg_price = sum(prices) / len(prices)
            Trade.objects.create(
                symbol=symbol.upper(),
                price=avg_price,
                trade_time=timezone.now(),
                quantity=volume
            )  # save average price of trades to the database

            r.delete(trades_key)  # clear the trades from Redis
