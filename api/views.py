from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from api.models import TickerAggregate
from api.serializers import TickerAggregateSerializer


class TickerHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TickerAggregate.objects.all()
    serializer_class = TickerAggregateSerializer
    pagination_class = LimitOffsetPagination


def websocket_test(request):
    return render(request, 'websocket_test.html')
