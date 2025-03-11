from rest_framework import viewsets

from api.models import TickerAggregate
from api.serializers import TickerAggregateSerializer


class TickerHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TickerAggregate.objects.all()
    serializer_class = TickerAggregateSerializer
