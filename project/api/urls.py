from django.urls import path, include

from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from api.views import (
    UsuarioViewSet, PedidoViewSet,
    ProdutoViewSet, PedidoProdutoViewSet,
    TokenObtainPairView)

router = routers.DefaultRouter()
router.register(
    'produtos', ProdutoViewSet,
    basename='produtos')
router.register(
    'usuarios', UsuarioViewSet,
    basename='usuarios')
router.register(
    'pedidos', PedidoViewSet,
    basename='pedidos')

pedidos_produtos_router = routers.NestedSimpleRouter(
    router, 'pedidos', lookup='pedidos')
pedidos_produtos_router.register(
    'produtos', PedidoProdutoViewSet,
    basename='produtos')

urlpatterns = [
    path('token/',
        TokenObtainPairView.as_view(),
            name='token_obtain_pair'),
    path('token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'),
    path('', include(router.urls)),
    path('', include(pedidos_produtos_router.urls)),
]
