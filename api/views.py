from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import PermissionDenied

from rest_framework_simplejwt.views import TokenViewBase

from api.serializers import (
    UsuarioSerializer,
    ProdutoSerializer,
    PedidoSerializer,
    PedidoProdutoSerializer,
    TokenSerializer,
)
from app.models import Usuario, Produto, Pedido, PedidoProduto

# Create your views here.


class PermissionsModelViewSet(viewsets.ModelViewSet):
    permission_dict = {}

    def get_permissions(self):
        action = self.action
        try:
            permissions = self.permission_dict[action]
            return [permission() for permission in permissions]
        except KeyError:
            return [permission() for permission in self.permission_classes]


class UsuarioViewSet(PermissionsModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_dict = {"create": [],"list":[IsAdminUser]}

    def retrieve(self, request, pk=None):
        pk = int(pk)
        queryset = self.get_queryset()
        if pk != self.request.user.pk:
            raise PermissionDenied
        usuario = get_object_or_404(queryset, pk=pk)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)


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

    def retrieve(self, request, pk=None):
        pk = int(pk)
        queryset = Pedido.objects.filter(usuario=request.user)
        pedido = get_object_or_404(queryset, pk=pk)
        serializer = PedidoSerializer(pedido)
        return Response(serializer.data)


class PedidoProdutoViewSet(PermissionsModelViewSet):
    serializer_class = PedidoProdutoSerializer
    queryset = PedidoProduto.objects.all()

    def list(self, request, pedidos_pk=None):
        queryset = Pedido.objects.filter(usuario=request.user)
        pedido = get_object_or_404(queryset, pk=pedidos_pk)
        queryset = PedidoProduto.objects.filter(pedido=pedido)
        serializer = PedidoProdutoSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, pedidos_pk=None):
        queryset = Pedido.objects.filter(usuario=request.user)
        pedido = get_object_or_404(queryset, pk=pedidos_pk)
        queryset = PedidoProduto.objects.filter(pedido=pedido)
        pedido_produto = get_object_or_404(queryset, pk=pk)
        serializer = PedidoProdutoSerializer(pedido_produto)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        pedidos_pk = self.kwargs["pedidos_pk"]
        queryset = Pedido.objects.filter(usuario=self.request.user)
        pedido = get_object_or_404(queryset, pk=pedidos_pk)
        context.update({"pedidos_pk": pedidos_pk})
        return context


class TokenObtainPairView(TokenViewBase):
    serializer_class = TokenSerializer
