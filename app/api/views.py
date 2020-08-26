from app.models import Pedido, PedidoProduto, Produto, Usuario
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from .serializers import (
    PedidoProdutoSerializer,
    PedidoSerializer,
    ProdutoSerializer,
    TokenSerializer,
    UsuarioSerializer,
)


class PermissionsModelViewSet(viewsets.ModelViewSet):
    permission_dict = {}

    def get_permissions(self):
        try:
            action = self.action
            permissions = self.permission_dict[action]
            return [permission() for permission in permissions]
        except (KeyError, AttributeError):
            return [permission() for permission in self.permission_classes]


class UsuarioViewSet(PermissionsModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_dict = {"create": [], "list": [IsAdminUser]}

    def get_object(self):
        pk = self.kwargs.get("pk")
        queryset = self.get_queryset()
        if str(pk) != str(self.request.user.pk):
            raise PermissionDenied
        obj = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj


class ProdutoViewSet(PermissionsModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    permission_dict = {
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "partial_update": [IsAdminUser],
        "destroy": [IsAdminUser],
        "list": [],
        "retrieve": [],
    }


class PedidoViewSet(PermissionsModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def list(self, request):
        queryset = Pedido.objects.filter(usuario=request.user)
        serializer = PedidoSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_object(self):
        queryset = Pedido.objects.filter(usuario=self.request.user)
        obj = get_object_or_404(queryset, pk=self.kwargs.get("pk"))
        self.check_object_permissions(self.request, obj)
        return obj


class PedidoProdutoViewSet(PermissionsModelViewSet):
    serializer_class = PedidoProdutoSerializer
    queryset = PedidoProduto.objects.all()

    def list(self, request, pedidos_pk=None):
        queryset = Pedido.objects.filter(usuario=request.user)
        pedido = get_object_or_404(queryset, pk=pedidos_pk)
        queryset = PedidoProduto.objects.filter(pedido=pedido)
        serializer = PedidoProdutoSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pedido__pk=self.kwargs["pedidos_pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        pedidos_pk = self.kwargs["pedidos_pk"]
        queryset = Pedido.objects.filter(usuario=self.request.user)
        get_object_or_404(queryset, pk=pedidos_pk)
        context.update({"pedidos_pk": pedidos_pk})
        return context


class TokenObtainPairView(TokenViewBase):
    serializer_class = TokenSerializer
