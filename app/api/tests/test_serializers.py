from rest_framework.test import APITransactionTestCase

from app.models import Usuario
from app.tests.test_models import (
    mock_usuario,
    mock_produto,
    mock_pedido,
    mock_pedidoProduto,
)
from app.api.tests.test_views import mock_request
from app.api.serializers import (
    TokenSerializer,
    UsuarioSerializer,
    ProdutoSerializer,
    PedidoSerializer,
    PedidoProdutoSerializer,
)


class TestTokenSerializer(APITransactionTestCase):
    username_field = Usuario.EMAIL_FIELD

    def test_username_field(self):
        self.assertEqual(TokenSerializer.username_field, Usuario.EMAIL_FIELD)


class TestUsuarioSerializer(APITransactionTestCase):
    username_field = Usuario.EMAIL_FIELD

    def setUp(self):
        self.usuario_data = mock_usuario(False)["data"]

    def test_cpf(self):
        serializer = UsuarioSerializer(data=self.usuario_data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn("cpf", serializer.errors)

        self.usuario_data["cpf"] = "0000.000-00"
        serializer = UsuarioSerializer(data=self.usuario_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("cpf", serializer.errors)

    def test_rg(self):
        serializer = UsuarioSerializer(data=self.usuario_data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn("rg", serializer.errors)

        self.usuario_data["rg"] = "test"
        serializer = UsuarioSerializer(data=self.usuario_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rg", serializer.errors)

    def test_password_hash_create(self):
        serializer = UsuarioSerializer(data=self.usuario_data)
        self.assertTrue(serializer.is_valid())
        saved_usuario = serializer.save()
        self.assertNotEqual(saved_usuario, self.usuario_data["password"])

        usuario = serializer.instance
        serializer = UsuarioSerializer(
            usuario, data=self.usuario_data, partial=True
        )
        self.assertTrue(serializer.is_valid())
        saved_usuario = serializer.save()
        self.assertNotEqual(saved_usuario, self.usuario_data["password"])

    def test_exclude(self):
        self.usuario_data["deleted"] = True
        serializer = UsuarioSerializer(data=self.usuario_data)
        self.assertNotIn("deleted", serializer.fields.keys())

    def test_password_write_only(self):
        serializer = UsuarioSerializer(data=self.usuario_data)
        self.assertTrue(serializer.fields["password"].write_only)


class TestProdutoSerializer(APITransactionTestCase):
    def setUp(self):
        self.produto_data = mock_produto(False)["data"]

    def test_exclude(self):
        self.produto_data["deleted"] = True
        serializer = ProdutoSerializer(data=self.produto_data)
        self.assertNotIn("deleted", serializer.fields.keys())


class TestPedidoSerializer(APITransactionTestCase):
    def setUp(self):
        mock_dict = mock_pedido(create=False)
        self.usuario = mock_dict["usuario"]
        self.pedido_data = mock_dict["data"]

    def test_exclude(self):
        self.pedido_data["deleted"] = True
        serializer = PedidoSerializer(data=self.pedido_data)
        self.assertNotIn("deleted", serializer.fields.keys())

    def test_usuario_read_only(self):
        request = mock_request(self.usuario)
        serializer = PedidoSerializer(
            data=self.pedido_data, context={"request": request}
        )

        self.assertTrue(serializer.fields["usuario"].read_only)

    def test_create_update(self):
        request = mock_request(self.usuario)
        serializer = PedidoSerializer(
            data=self.pedido_data, context={"request": request}
        )
        self.assertTrue(serializer.is_valid())
        pedido = serializer.save()
        self.assertEqual(pedido.usuario, self.usuario)

        serializer = PedidoSerializer(
            pedido,
            data=self.pedido_data,
            context={"request": request},
            partial=True,
        )
        self.assertTrue(serializer.is_valid())
        pedido = serializer.save()
        self.assertEqual(pedido.usuario, self.usuario)


class TestPedidoProdutoSerializer(APITransactionTestCase):
    def setUp(self):
        mock_dict = mock_pedidoProduto(create=False)
        self.usuario = mock_dict["usuario"]
        self.pedido = mock_dict["data"]["pedido"]
        self.produto = mock_dict["data"]["produto"]
        self.pedProduto_data = mock_dict["data"]

        self.pedProduto_data["produto"] = self.pedProduto_data["produto"].pk
        self.pedProduto_data["pedido"] = self.pedProduto_data["pedido"].pk

    def test_exclude(self):
        self.pedProduto_data["deleted"] = True
        serializer = PedidoProdutoSerializer(data=self.pedProduto_data)
        self.assertNotIn("deleted", serializer.fields.keys())

    def test_create_update(self):
        request = mock_request(self.usuario)
        serializer = PedidoProdutoSerializer(
            data=self.pedProduto_data,
            context={"request": request, "pedidos_pk": self.pedido.pk},
        )
        self.assertTrue(serializer.is_valid())
        pedidoProduto = serializer.save()
        self.assertEqual(pedidoProduto.pedido, self.pedido)
        self.assertEqual(pedidoProduto.produto, self.produto)

        serializer = PedidoProdutoSerializer(
            pedidoProduto,
            data=self.pedProduto_data,
            context={"request": request, "pedidos_pk": self.pedido.pk},
        )
        self.assertTrue(serializer.is_valid())
        pedidoProduto = serializer.save()
        self.assertEqual(pedidoProduto.pedido, self.pedido)
        self.assertEqual(pedidoProduto.produto, self.produto)
