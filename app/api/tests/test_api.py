from rest_framework.test import APILiveServerTestCase

from app.models import Usuario
from app.tests.test_models import (
    mock_usuario,
    mock_superusuario,
    mock_pedido,
    mock_produto,
    mock_pedidoProduto,
)


class BaseTestCase(APILiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.obtain_token_url = cls.live_server_url + "/api/token/"

    def setUp(self):
        self.user_data = mock_usuario()["data"]
        self.superuser_data = mock_superusuario()["data"]


class AuthenticatedTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.obtain_token_url = cls.live_server_url + "/api/token/"

    def setUp(self):
        super().setUp()

        request = self.client.post(
            self.obtain_token_url, self.user_data, format="json"
        )
        self.user_token = request.json()["access"]

        request = self.client.post(
            self.obtain_token_url, self.superuser_data, format="json"
        )
        self.superuser_token = request.json()["access"]

    def authenticate_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_token)

    def authenticate_superuser(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.superuser_token
        )


class TokenTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.refresh_token_url = cls.live_server_url + "/api/token/refresh/"

    def test_get_token_fail_auth(self):
        """Endpoint must return 401 on failed authentication attempt"""
        request = self.client.post(
            self.obtain_token_url,
            {"email": "test2@test.com", "password": "t2est"},
            format="json",
        )
        self.assertEqual(request.status_code, 401)

    def test_get_token_success(self):
        request = self.client.post(
            self.obtain_token_url, self.user_data, format="json"
        )
        result_json = request.json()
        self.assertEqual(request.status_code, 200)
        self.assertIn("refresh", result_json)
        self.assertIn("access", result_json)

    def test_refresh_token_success(self):
        request = self.client.post(
            self.obtain_token_url, self.user_data, format="json"
        )
        self.assertEqual(request.status_code, 200)
        result_json = request.json()
        self.assertIn("access", result_json)


class UsuarioTestCase(AuthenticatedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.usuario_url = cls.live_server_url + "/api/usuarios/"

    def setUp(self):
        super().setUp()
        usuario_id = Usuario.objects.get(email=self.user_data["email"]).pk
        self.usuario_detail_url = self.usuario_url + f"{usuario_id}/"

    def test_get_list(self):
        """GET at api/usuarios/ must allow only superusers"""
        self.authenticate_user()
        request = self.client.get(self.usuario_url, format="json")
        self.assertEqual(request.status_code, 403)

        self.authenticate_superuser()
        request = self.client.get(self.usuario_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

    def test_post_list(self):
        """POST at api/usuarios/ must allow any"""
        usuario_data = mock_usuario(False)["data"]
        usuario_data["email"] = "test@test.com"
        usuario_data["username"] = "test"

        request = self.client.post(
            self.usuario_url, usuario_data, format="json"
        )
        self.assertEqual(request.status_code, 201)

    def test_detail(self):
        """User must be authenticated and data is user-restricted"""
        request = self.client.get(self.usuario_detail_url, format="json")
        self.assertEqual(request.status_code, 401)

        self.authenticate_user()
        request = self.client.get(self.usuario_detail_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

        usuario_data = {
            "username": self.user_data["username"],
            "email": self.user_data["email"],
            "password": self.user_data["password"],
            "cpf": "213.111.333-22",
            "rg": "1231212",
            "endereco": "test",
        }
        request = self.client.put(
            self.usuario_detail_url, usuario_data, format="json"
        )
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

        request = self.client.patch(
            self.usuario_detail_url, usuario_data, format="json"
        )
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

        request = self.client.delete(self.usuario_detail_url, format="json")
        self.assertEqual(request.status_code, 204)


class ProdutoTestCase(AuthenticatedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.produto_url = cls.live_server_url + "/api/produtos/"

    def setUp(self):
        super().setUp()
        produto_id = mock_produto()["produto"].pk
        self.produto_detail_url = self.produto_url + f"{produto_id}/"

    def test_get_produto(self):
        """GET at api/produtos/ must allow any"""
        request = self.client.get(self.produto_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

        request = self.client.get(self.produto_detail_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

    def test_non_safe_produto(self):
        """Superuser only"""
        produto_data = mock_produto()["data"]
        request = self.client.post(
            self.produto_url, produto_data, format="json"
        )
        self.assertEqual(request.status_code, 401)

        self.authenticate_user()
        request = self.client.post(
            self.produto_url, produto_data, format="json"
        )
        self.assertEqual(request.status_code, 403)

        self.authenticate_superuser()
        request = self.client.post(
            self.produto_url, produto_data, format="json"
        )
        self.assertEqual(request.status_code, 201)

        request = self.client.put(
            self.produto_detail_url, produto_data, format="json"
        )
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

        request = self.client.patch(
            self.produto_detail_url, produto_data, format="json"
        )
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

        request = self.client.delete(self.produto_detail_url, format="json")
        self.assertEqual(request.status_code, 204)


class PedidoTestCase(AuthenticatedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pedido_url = cls.live_server_url + "/api/pedidos/"

    def setUp(self):
        super().setUp()
        mock_dict = mock_pedido()
        self.usuario = mock_dict["usuario"]
        pedido_id = mock_dict["pedido"].pk
        self.pedido_detail_url = self.pedido_url + f"{pedido_id}/"

    def test_get_pedido(self):
        """User-restricted"""
        request = self.client.get(self.pedido_url, format="json")
        self.assertEqual(request.status_code, 401)

        self.authenticate_superuser()
        request = self.client.get(self.pedido_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.json(), [])

        self.authenticate_user()
        request = self.client.get(self.pedido_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

        request = self.client.get(self.pedido_detail_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

    def test_non_safe_pedido(self):
        """User-restricted"""
        pedido_data = {"usuario": self.usuario.pk, "endereco": "test"}

        request = self.client.post(self.pedido_url, pedido_data, format="json")
        self.assertEqual(request.status_code, 401)

        self.authenticate_user()
        request = self.client.post(self.pedido_url, pedido_data, format="json")
        self.assertEqual(request.status_code, 201)

        request = self.client.put(
            self.pedido_detail_url, pedido_data, format="json"
        )
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

        request = self.client.patch(
            self.pedido_detail_url, pedido_data, format="json"
        )
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

        request = self.client.delete(self.pedido_detail_url, format="json")
        self.assertEqual(request.status_code, 204)


class PedidoProdutosTestCase(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        mock_dict = mock_pedidoProduto()
        self.usuario = mock_dict["usuario"]
        self.pedido = mock_dict["data"]["pedido"]
        self.produto = mock_dict["data"]["produto"]

        self.pedProduto_url = (
            self.live_server_url + f"/api/pedidos/{self.pedido.pk}/produtos/"
        )
        self.pedProduto_detail_url = self.pedProduto_url + f"{self.produto.pk}/"

        self.pedProduto_data = {
            "pedido": self.pedido.pk,
            "produto": self.produto.pk,
            "quantidade": 2,
        }

    def test_get_pedidoProduto(self):
        """User-restricted"""
        request = self.client.get(self.pedProduto_url, format="json")
        self.assertEqual(request.status_code, 401)

        self.authenticate_superuser()
        request = self.client.get(self.pedProduto_url, format="json")
        self.assertEqual(request.status_code, 404)

        self.authenticate_user()
        request = self.client.get(self.pedProduto_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertNotEqual(request.json(), [])

        request = self.client.get(self.pedProduto_detail_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

    def test_non_safe_pedidoProduto_url(self):
        """User-restricted"""
        request = self.client.post(
            self.pedProduto_url, self.pedProduto_data, format="json"
        )
        self.assertEqual(request.status_code, 401)

        self.authenticate_user()
        self.client.get(
            self.pedProduto_detail_url, self.pedProduto_data, format="json"
        )

        request = self.client.put(
            self.pedProduto_detail_url, self.pedProduto_data, format="json"
        )
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

        request = self.client.patch(
            self.pedProduto_detail_url, self.pedProduto_data, format="json"
        )
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json())

        request = self.client.delete(self.pedProduto_detail_url, format="json")
        self.assertEqual(request.status_code, 204)

        self.pedProduto_data["produto"] = mock_produto()["produto"].pk
        request = self.client.post(
            self.pedProduto_url, self.pedProduto_data, format="json"
        )
        self.assertEqual(request.status_code, 201)
