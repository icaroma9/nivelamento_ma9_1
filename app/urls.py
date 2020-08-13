from django.urls import path, include

from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenRefreshView

from app.api.views import (
    UsuarioViewSet,
    PedidoViewSet,
    ProdutoViewSet,
    PedidoProdutoViewSet,
    TokenObtainPairView,
)


router = routers.DefaultRouter()
router.register("produtos", ProdutoViewSet, basename="produtos")
router.register("pedidos", PedidoViewSet, basename="pedidos")
router.register("usuarios", UsuarioViewSet, basename="usuarios")

pedidos_produtos_router = routers.NestedSimpleRouter(
    router, "pedidos", lookup="pedidos"
)
pedidos_produtos_router.register(
    "produtos", PedidoProdutoViewSet, basename="produtos"
)

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/", include(router.urls)),
    path("api/", include(pedidos_produtos_router.urls)),
]
