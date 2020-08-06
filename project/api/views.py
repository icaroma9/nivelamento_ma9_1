from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenViewBase

from api.serializers import (
    UsuarioSerializer, ProdutoSerializer,
    PedidoSerializer, PedidoProdutoSerializer,
    TokenSerializer)
from app.models import (
    Usuario, Produto, Pedido, PedidoProduto)

# Create your views here.

class UsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = Usuario.objects.all()

class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer
    queryset = Produto.objects.all()

class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    queryset = Pedido.objects.all()

    def list(self, request):
        queryset = Pedido.objects.filter(usuario=request.user)
        serializer = PedidoSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Pedido.objects.filter(
            usuario=request.user)
        pedido = get_object_or_404(queryset, pk=pk)
        serializer = PedidoSerializer(pedido)
        return Response(serializer.data)

class PedidoProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoProdutoSerializer
    queryset = PedidoProduto.objects.all()

    def list(self, request,
            pedidos_pk=None):
        queryset = Pedido.objects.filter(
            usuario=request.user)
        pedido = get_object_or_404(queryset, pk=pedidos_pk)
        queryset = PedidoProduto.objects.filter(
            pedido=pedido)
        serializer = PedidoProdutoSerializer(
            queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request,
            pk=None, pedidos_pk=None):
        queryset = Pedido.objects.filter(
            usuario=request.user)
        pedido = get_object_or_404(queryset, pk=pedidos_pk)
        queryset = PedidoProduto.objects.filter(
            pedido=pedido)
        pedido_produto = get_object_or_404(queryset, pk=pk)
        serializer = PedidoProdutoSerializer(pedido_produto)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        pedidos_pk = self.kwargs['pedidos_pk']
        queryset = Pedido.objects.filter(
            usuario=self.request.user)
        pedido = get_object_or_404(queryset, pk=pedidos_pk)
        context.update({"pedidos_pk": pedidos_pk})
        return context

class TokenObtainPairView(TokenViewBase):
    serializer_class = TokenSerializer
