from django.contrib import admin

from api.models import Trade, TickerAggregate


class TradeAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'price', 'quantity', 'trade_time')
    search_fields = ('symbol', 'trade_time')
    list_filter = ('symbol', 'trade_time')


class TickerAggregateAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'start_time', 'end_time', 'open_price', 'close_price', 'high_price', 'low_price', 'volume')
    search_fields = ('symbol', 'start_time')
    list_filter = ('symbol', 'start_time')


admin.site.register(Trade, TradeAdmin)
admin.site.register(TickerAggregate, TickerAggregateAdmin)

