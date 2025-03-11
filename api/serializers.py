from rest_framework import serializers

from api.models import TickerAggregate


class TickerAggregateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TickerAggregate
        fields = '__all__'
