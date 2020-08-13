from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction

from app.models import Usuario, Pedido, Produto, PedidoProduto


def mock_usuario(create=True):
    result = {}
    result["data"] = {
        "username": "x",
        "email": "x@x.com",
        "password": "x",
        "cpf": "213.111.333-22",
        "rg": "1231212",
        "endereco": "x",
    }
    if create:
        try:
            with transaction.atomic():
                usuario = Usuario.objects.create_user(**result["data"])
        except IntegrityError:
            usuario = Usuario.objects.get(email=result["data"]["email"])
        result["usuario"] = usuario
    return result


def mock_superusuario(create=True):
    result = {}
    result["data"] = {
        "username": "x2",
        "email": "x2@x.com",
        "password": "x",
        "cpf": "213.111.333-22",
        "rg": "1231212",
        "endereco": "x",
    }
    if create:
        result["usuario"] = Usuario.objects.create_superuser(**result["data"])
    return result


def mock_produto(create=True):
    result = {}
    result["data"] = {
        "nome": "x",
        "descricao": "x",
    }

    if create:
        result["produto"] = Produto.objects.create(**result["data"])
    return result


def mock_pedido(create=True):
    result_usuario = mock_usuario()

    result = {}
    result["usuario"] = result_usuario["usuario"]
    result["data"] = {
        "usuario": result["usuario"],
        "endereco": "x",
    }

    if create:
        result["pedido"] = Pedido.objects.create(**result["data"])
    return result


def mock_pedidoProduto(create=True):
    result_pedido = mock_pedido()
    result_produto = mock_produto()

    result = {}
    result["usuario"] = result_pedido["usuario"]
    result["data"] = {
        "produto": result_produto["produto"],
        "pedido": result_pedido["pedido"],
        "quantidade": 1,
    }

    if create:
        result["pedidoProduto"] = PedidoProduto.objects.create(**result["data"])
    return result


class UsuarioTestCase(TestCase):
    def setUp(self):
        mock_dict = mock_usuario()
        self.data = mock_dict["data"]
        self.usuario = mock_dict["usuario"]

    def test_str(self):
        self.assertEqual(str(self.usuario), self.usuario.email)


class ProdutoTestCase(TestCase):
    def setUp(self):
        mock_dict = mock_produto()
        self.data = mock_dict["data"]
        self.produto = mock_dict["produto"]

    def test_str(self):
        self.assertEqual(str(self.produto), self.produto.nome)


class PedidoTestCase(TestCase):
    def setUp(self):
        mock_dict = mock_pedido()
        self.data = mock_dict["data"]
        self.pedido = mock_dict["pedido"]

    def test_str(self):
        self.assertEqual(str(self.pedido), str(self.pedido.feito))

    def test_cascade(self):
        self.assertTrue(Pedido.objects.all())
        self.data["usuario"].delete()
        self.assertFalse(Pedido.objects.all())


class PedidoProdutoTestCase(TestCase):
    def setUp(self):
        mock_dict = mock_pedidoProduto()
        self.data = mock_dict["data"]
        self.pedidoProduto = mock_dict["pedidoProduto"]

    def test_str(self):
        self.assertEqual(
            str(self.pedidoProduto),
            f"{self.pedidoProduto.produto} x{self.pedidoProduto.quantidade}",
        )

    def test_cascade_produto(self):
        self.assertTrue(PedidoProduto.objects.all())
        self.data["produto"].delete()
        self.assertFalse(PedidoProduto.objects.all())

    def test_cascade_pedido(self):
        self.assertTrue(PedidoProduto.objects.all())
        self.data["pedido"].delete()
        self.assertFalse(PedidoProduto.objects.all())

    def test_unique(self):
        with self.assertRaises(IntegrityError):
            PedidoProduto.objects.create(**self.data)
