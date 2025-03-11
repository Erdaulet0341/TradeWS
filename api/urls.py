from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from TradeWS.variables import get_env_variable
from api import views
from api.views import TickerHistoryViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="TradeWS API",
        default_version='v1',
        description="API documentation",
        license=openapi.License(name="Yerdaulet License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    url=get_env_variable('BASE_URL')
)

router = DefaultRouter()
router.register(r'trades', TickerHistoryViewSet, basename='trade')

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # for Swagger UI

    path('', include(router.urls)),

    path('websocket-test/', views.websocket_test, name='websocket_test')  # for testing WebSocket
]
