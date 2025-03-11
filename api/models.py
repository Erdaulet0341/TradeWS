from django.db import models


class Trade(models.Model):
    symbol = models.CharField("Торговая пара", max_length=10, db_index=True)
    price = models.DecimalField("Цена", max_digits=20, decimal_places=10)
    quantity = models.DecimalField("Объём", max_digits=20, decimal_places=10)
    trade_time = models.DateTimeField("Время сделки", db_index=True)

    class Meta:
        ordering = ['-trade_time']


class TickerAggregate(models.Model):
    symbol = models.CharField("Торговая пара", max_length=10, db_index=True)
    start_time = models.DateTimeField("Начало интервала", db_index=True)
    end_time = models.DateTimeField("Конец интервала")
    open_price = models.DecimalField("Открытие", max_digits=20, decimal_places=10)
    close_price = models.DecimalField("Закрытие", max_digits=20, decimal_places=10)
    high_price = models.DecimalField("Максимум", max_digits=20, decimal_places=10)
    low_price = models.DecimalField("Минимум", max_digits=20, decimal_places=10)
    volume = models.DecimalField("Объём", max_digits=20, decimal_places=10)

    class Meta:
        ordering = ['-start_time']
