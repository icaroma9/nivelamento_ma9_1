from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from app.api.views import (
    UsuarioViewSet,
    PedidoViewSet,
    ProdutoViewSet,
    PedidoProdutoViewSet,
    TokenObtainPairView,
)


router = DefaultRouter()
router.register("produtos", ProdutoViewSet)
router.register("pedidos", PedidoViewSet)
router.register("usuarios", UsuarioViewSet)

router.register(
    r"pedidos/(?P<pedidos_pk>[^/.]+)/produtos", PedidoProdutoViewSet
)

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path(
        "api/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"
    ),
    path("api/", include(router.urls)),
]
