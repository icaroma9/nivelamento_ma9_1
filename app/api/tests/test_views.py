from unittest.mock import Mock

from app.api.views import (
    PedidoProdutoViewSet,
    PedidoViewSet,
    PermissionsModelViewSet,
    UsuarioViewSet,
)
from app.tests.test_models import mock_pedido, mock_pedidoProduto, mock_usuario
from rest_framework.permissions import IsAdminUser
from rest_framework.test import APITransactionTestCase


def mock_request(usuario):
    request = Mock()
    request.user = usuario
    return request


def mock_view(view, request, *args, **kwargs):
    """Mimics as_view() functionality"""
    view.request = request
    view.args = args
    view.kwargs = kwargs
    view.format_kwarg = Mock()
    return view


class TestPermissionsModelViewSet(APITransactionTestCase):
    def test_get_permissions(self):
        permissionView = PermissionsModelViewSet()
        permissionView.permission_dict = {
            "list": [IsAdminUser],
        }
        permissionView.action = "list"
        permissions = permissionView.get_permissions()
        self.assertEqual(len(permissions), 1)
        list_permission = permissionView.get_permissions()[0]
        self.assertIsInstance(list_permission, IsAdminUser)


class TestUsuarioViewSet(APITransactionTestCase):
    def setUp(self):
        self.usuario = mock_usuario()["usuario"]

        self.viewSet = UsuarioViewSet()
        self.request = mock_request(self.usuario)
        self.view = mock_view(self.viewSet, self.request)

    def test_retrieve(self):
        view = mock_view(self.viewSet, self.request, pk=self.usuario.pk)
        response = view.retrieve(self.request, pk=self.usuario.pk)
        self.assertEqual(response.status_code, 200)


class TestPedidoViewSet(APITransactionTestCase):
    def setUp(self):
        mock_dict = mock_pedido()
        self.usuario = mock_dict["usuario"]
        self.pedido = mock_dict["pedido"]

        self.viewSet = PedidoViewSet()
        self.request = mock_request(self.usuario)
        self.view = mock_view(self.viewSet, self.request)

    def test_retrieve(self):
        view = mock_view(self.viewSet, self.request, pk=self.pedido.pk)
        response = view.retrieve(self.request, pk=self.pedido.pk)
        self.assertEqual(response.status_code, 200)

    def test_list(self):
        response = self.view.list(self.request)
        self.assertEqual(response.status_code, 200)


class TestPedidoProdutoViewSet(APITransactionTestCase):
    def setUp(self):
        mock_dict = mock_pedidoProduto()
        self.usuario = mock_dict["usuario"]
        self.pedido = mock_dict["data"]["pedido"]
        self.produto = mock_dict["data"]["produto"]

        self.viewSet = PedidoProdutoViewSet()
        self.request = mock_request(self.usuario)
        self.view = mock_view(
            self.viewSet, self.request, pedidos_pk=self.pedido.pk
        )

    def test_retrieve(self):
        response = self.view.retrieve(
            self.request, pk=self.produto.pk, pedidos_pk=self.pedido.pk
        )
        self.assertEqual(response.status_code, 200)

    def test_list(self):
        response = self.view.list(self.request, pedidos_pk=self.pedido.pk)
        self.assertEqual(response.status_code, 200)

    def test_get_serializer_context(self):
        context = self.view.get_serializer_context()
        self.assertIn("pedidos_pk", context)
