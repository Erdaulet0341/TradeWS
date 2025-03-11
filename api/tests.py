import json
from unittest.mock import patch, MagicMock, AsyncMock
from decimal import Decimal
from datetime import datetime, timedelta

import pytest
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.layers import get_channel_layer

from TradeWS.tasks import aggregate_trades
from api.models import Trade, TickerAggregate
from api.routing import websocket_urlpatterns
from api.serializers import TickerAggregateSerializer


class BinanceWebSocketTest(TestCase):  # Tests for connecting to Binance WebSocket.

    @patch('websockets.connect')
    @patch('redis.Redis')
    @patch('asyncio.get_event_loop')
    def test_binance_management_command(self, mock_loop, mock_redis, mock_websocket_connect):
        from django.core.management import call_command
        from io import StringIO

        mock_loop_instance = MagicMock()
        mock_loop.return_value = mock_loop_instance

        mock_websocket = AsyncMock()
        mock_websocket.__aenter__.return_value = mock_websocket
        mock_websocket_connect.return_value = mock_websocket

        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance

        output = StringIO()
        call_command('listen_binance', stdout=output)

        mock_loop_instance.run_until_complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_binance_websocket_connection(self):
        from TradeWS.variables import SYMBOLS

        mock_websocket = AsyncMock()

        with patch('websockets.connect', return_value=mock_websocket):
            from api.management.commands.binance_listener import Command
            command = Command()

            mock_websocket.__aenter__.return_value.recv = AsyncMock(side_effect=Exception("Test exit"))

            try:
                await command.listen_binance()
            except Exception as e:
                if str(e) != "Test exit":
                    raise

            mock_websocket.__aenter__.assert_called_once()

            expected_subscribe_message = {
                "method": "SUBSCRIBE",
                "params": [f"{symbol}@trade" for symbol in SYMBOLS],
                "id": 1
            }
            mock_websocket.__aenter__.return_value.send.assert_called_once_with(json.dumps(expected_subscribe_message))

    @pytest.mark.asyncio
    async def test_binance_message_processing(self):
        from TradeWS.variables import BINANCE_WS_URL, SYMBOLS, TIME_INTERVAL

        mock_websocket = AsyncMock()
        mock_redis_instance = MagicMock()

        test_message = json.dumps({
            "e": "trade",
            "s": "BTCUSDT",
            "p": "45000.00",
            "q": "0.5",
            "T": int(datetime.now().timestamp() * 1000)
        })

        mock_websocket.__aenter__.return_value.__aiter__.return_value = [test_message]

        with patch('websockets.connect', return_value=mock_websocket), \
                patch('redis.Redis', return_value=mock_redis_instance):

            from api.management.commands.binance_listener import Command
            command = Command()

            with patch.object(command, 'listen_binance', side_effect=Exception("Test exit")):
                try:
                    await command.listen_binance()
                except Exception as e:
                    if str(e) != "Test exit":
                        raise

            mock_redis_instance.lpush.assert_called_once()

            call_args = mock_redis_instance.lpush.call_args[0]
            self.assertTrue(call_args[0].startswith('trades:'))

            saved_data = json.loads(call_args[1])
            self.assertEqual(saved_data['symbol'], 'btcusdt')
            self.assertEqual(saved_data['price'], '45000.00')
            self.assertEqual(saved_data['quantity'], '0.5')
            self.assertIn('trade_time', saved_data)

            mock_redis_instance.ltrim.assert_called_once()
            ltrim_args = mock_redis_instance.ltrim.call_args[0]
            self.assertEqual(ltrim_args[1], 0)
            self.assertEqual(ltrim_args[2], TIME_INTERVAL)


class CeleryTasksTest(TestCase):  # Tests for Celery tasks.

    @patch('redis.Redis')
    def test_aggregate_trades_task(self, mock_redis):
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance

        test_symbol = "BTCUSDT"
        test_trades = [
            json.dumps({
                "symbol": test_symbol,
                "price": "45000.00",
                "quantity": "0.5",
                "trade_time": str(int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000))
            }),
            json.dumps({
                "symbol": test_symbol,
                "price": "45100.00",
                "quantity": "0.3",
                "trade_time": str(int((datetime.now() - timedelta(minutes=2)).timestamp() * 1000))
            }),
            json.dumps({
                "symbol": test_symbol,
                "price": "45200.00",
                "quantity": "0.7",
                "trade_time": str(int(datetime.now().timestamp() * 1000))
            })
        ]

        mock_redis_instance.lrange.return_value = test_trades

        with patch('api.tasks.SYMBOLS', [test_symbol]):
            aggregate_trades()

            mock_redis_instance.lrange.assert_called_with(f"trades:{test_symbol}", 0, -1)
            mock_redis_instance.delete.assert_called_with(f"trades:{test_symbol}")

            ticker = TickerAggregate.objects.get(symbol=test_symbol.upper())
            self.assertEqual(ticker.high_price, Decimal('45200.00'))
            self.assertEqual(ticker.low_price, Decimal('45000.00'))
            self.assertEqual(ticker.open_price, Decimal('45000.00'))
            self.assertEqual(ticker.close_price, Decimal('45200.00'))
            self.assertEqual(ticker.volume, Decimal('1.5'))  # 0.5 + 0.3 + 0.7

            trade = Trade.objects.get(symbol=test_symbol.upper())
            avg_price = (45000.00 + 45100.00 + 45200.00) / 3
            self.assertEqual(float(trade.price), avg_price)
            self.assertEqual(float(trade.quantity), 1.5)


class RESTAPITest(TestCase):  # Tests for the REST API.

    def setUp(self):
        self.client = APIClient()
        self.test_symbol = "BTCUSDT"

        now = timezone.now()
        self.ticker1 = TickerAggregate.objects.create(
            symbol=self.test_symbol,
            start_time=now - timedelta(minutes=10),
            end_time=now - timedelta(minutes=5),
            open_price=Decimal('44000.00'),
            close_price=Decimal('44100.00'),
            high_price=Decimal('44200.00'),
            low_price=Decimal('43900.00'),
            volume=Decimal('2.5')
        )

        self.ticker2 = TickerAggregate.objects.create(
            symbol=self.test_symbol,
            start_time=now - timedelta(minutes=5),
            end_time=now,
            open_price=Decimal('44100.00'),
            close_price=Decimal('44300.00'),
            high_price=Decimal('44400.00'),
            low_price=Decimal('44050.00'),
            volume=Decimal('3.2')
        )

    def test_list_tickers(self):
        url = reverse('trade-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tickers = TickerAggregate.objects.all()
        serializer = TickerAggregateSerializer(tickers, many=True)
        expected_data = serializer.data

        self.assertEqual(len(response.data['results']), len(expected_data))

    def test_retrieve_ticker(self):
        url = reverse('trade-detail', kwargs={'pk': self.ticker2.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = TickerAggregateSerializer(self.ticker2)
        expected_data = serializer.data

        self.assertEqual(response.data, expected_data)

    def test_filter_by_symbol(self):
        url = f"{reverse('trade-list')}?symbol={self.test_symbol}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for item in response.data['results']:
            self.assertEqual(item['symbol'], self.test_symbol)

    def test_swagger_documentation(self):
        url = reverse('schema-swagger-ui')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'swagger')


@pytest.mark.asyncio
class WebSocketServerTest(TransactionTestCase):  # Tests for WebSocket server.

    async def setUp(self):
        self.test_symbol = "BTCUSDT"

        @database_sync_to_async
        def create_ticker():
            return TickerAggregate.objects.create(
                symbol=self.test_symbol,
                start_time=timezone.now() - timedelta(minutes=5),
                end_time=timezone.now(),
                open_price=Decimal('44100.00'),
                close_price=Decimal('44300.00'),
                high_price=Decimal('44400.00'),
                low_price=Decimal('44050.00'),
                volume=Decimal('3.2')
            )

        self.ticker = await create_ticker()

        self.application = URLRouter(websocket_urlpatterns)

    async def test_websocket_connection(self):
        communicator = WebsocketCommunicator(self.application, "/ws/trade/")
        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_receive_ticker_data(self):
        communicator = WebsocketCommunicator(self.application, "/ws/trade/")
        connected, _ = await communicator.connect()

        await communicator.send_json_to({
            "symbol": self.test_symbol
        })

        response = await communicator.receive_json_from()

        self.assertEqual(response["symbol"], self.test_symbol)
        self.assertEqual(response["open_price"], str(self.ticker.open_price))
        self.assertEqual(response["close_price"], str(self.ticker.close_price))
        self.assertEqual(response["high_price"], str(self.ticker.high_price))
        self.assertEqual(response["low_price"], str(self.ticker.low_price))
        self.assertEqual(response["volume"], str(self.ticker.volume))

        await communicator.disconnect()

    async def test_broadcast_updates(self):
        communicator1 = WebsocketCommunicator(self.application, "/ws/trade/")
        communicator2 = WebsocketCommunicator(self.application, "/ws/trade/")

        await communicator1.connect()
        await communicator2.connect()

        @database_sync_to_async
        def create_new_ticker():
            new_ticker = TickerAggregate.objects.create(
                symbol=self.test_symbol,
                start_time=timezone.now() - timedelta(minutes=2),
                end_time=timezone.now(),
                open_price=Decimal('44300.00'),
                close_price=Decimal('44500.00'),
                high_price=Decimal('44600.00'),
                low_price=Decimal('44250.00'),
                volume=Decimal('2.7')
            )
            return new_ticker

        new_ticker = await create_new_ticker()

        channel_layer = get_channel_layer()
        data = {
            "symbol": new_ticker.symbol,
            "open_price": str(new_ticker.open_price),
            "close_price": str(new_ticker.close_price),
            "high_price": str(new_ticker.high_price),
            "low_price": str(new_ticker.low_price),
            "volume": str(new_ticker.volume),
        }

        await channel_layer.group_send(
            "trades", {"type": "send_trade_update", "data": data}
        )

        response1 = await communicator1.receive_json_from()
        response2 = await communicator2.receive_json_from()

        for response in [response1, response2]:
            self.assertEqual(response["symbol"], self.test_symbol)
            self.assertEqual(response["open_price"], str(new_ticker.open_price))
            self.assertEqual(response["close_price"], str(new_ticker.close_price))
            self.assertEqual(response["high_price"], str(new_ticker.high_price))
            self.assertEqual(response["low_price"], str(new_ticker.low_price))
            self.assertEqual(response["volume"], str(new_ticker.volume))

        await communicator1.disconnect()
        await communicator2.disconnect()
