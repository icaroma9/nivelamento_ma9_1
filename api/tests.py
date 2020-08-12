from rest_framework.test import APILiveServerTestCase

from app.models import Usuario, Produto, Pedido, PedidoProduto

# Create your tests here.


class BaseTestCase(APILiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.obtain_token_url = cls.live_server_url + "/api/token/"
        cls.superuser_data = {
            "username": "test",
            "password": "test",
            "email": "test@test.com",
        }
        cls.user_data = {
            "username": "test2",
            "password": "test2",
            "email": "test2@test.com",
        }

    def setUp(self):
        Usuario.objects.create_user(**self.user_data)
        Usuario.objects.create_superuser(**self.superuser_data)


class AuthenticatedTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.obtain_token_url = cls.live_server_url + "/api/token/"

    def setUp(self):
        super().setUp()

        request = self.client.post(
            self.obtain_token_url, self.user_data, format="json",
        )
        self.user_token = request.json()["access"]

        request = self.client.post(
            self.obtain_token_url, self.superuser_data, format="json",
        )
        self.superuser_token = request.json()["access"]

    def authenticate_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_token)
    
    def authenticate_superuser(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.superuser_token)

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
            self.obtain_token_url, self.user_data, format="json",
        )
        result_json = request.json()
        self.assertEqual(request.status_code, 200)
        self.assertIn("refresh", result_json)
        self.assertIn("access", result_json)

    def test_refresh_token_success(self):
        request = self.client.post(
            self.obtain_token_url, self.user_data, format="json",
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
        usuario_id = Usuario.objects.get(email=self.user_data['email']).pk
        self.usuario_url_detail = self.usuario_url + f'{usuario_id}/'

    def test_get_ususario_list(self):
        """GET at api/usuarios/ must allow only superusers"""        
        self.authenticate_user()
        request = self.client.get(self.usuario_url, format="json")
        self.assertEqual(request.status_code, 403)

        self.authenticate_superuser()
        request = self.client.get(self.usuario_url, format="json")
        self.assertEqual(request.status_code, 200)

    def test_post_usuario_list(self):
        """POST at api/usuarios/ must allow any"""
        user_data = {
            "username":'test3',
            'email':'test3@test.com',
            'password':'test',
            'cpf':'213.111.333-22',
            'rg':'1231212',
            'endereco':'test'}
        request = self.client.post(self.usuario_url, 
            user_data, format="json")
        self.assertEqual(request.status_code, 201)

    def test_usuario_detail(self):
        """User must be authenticated and data is user-restricted"""
        request = self.client.get(self.usuario_url_detail, 
            format="json")
        self.assertEqual(request.status_code, 401)

        self.authenticate_user()
        request = self.client.get(self.usuario_url_detail, 
            format="json")
        self.assertEqual(request.status_code, 200)

        user_data = {
            "username":self.user_data['username'],
            'email':self.user_data['email'],
            'password':self.user_data['password'],
            'cpf':'213.111.333-22',
            'rg':'1231212',
            'endereco':'test'}
        request = self.client.put(self.usuario_url_detail, 
            user_data, format="json")
        self.assertEqual(request.status_code, 200)

        request = self.client.patch(self.usuario_url_detail, 
            user_data, format="json")
        self.assertEqual(request.status_code, 200)

        request = self.client.delete(self.usuario_url_detail, 
            format="json")
        self.assertEqual(request.status_code, 204)


class ProdutoTestCase(AuthenticatedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.produto_url = cls.live_server_url + "/api/produtos/"

    def setUp(self):
        super().setUp()
        produto_id = Produto.objects.create(
            nome='test',
            descricao='test').pk

        self.produto_url_detail = self.produto_url + f'{produto_id}/'

    def test_get_produto(self):
        """GET at api/produtos/ must allow any"""        
        request = self.client.get(self.produto_url, format="json")
        self.assertEqual(request.status_code, 200)

        request = self.client.get(self.produto_url_detail, format="json")
        self.assertEqual(request.status_code, 200)

    def test_non_safe_produto(self):
        """Superuser only"""
        produto_data = {
            'nome':'test2',
            'descricao':'test2'
        }
        request = self.client.post(self.produto_url, 
            produto_data, format="json")
        self.assertEqual(request.status_code, 401)

        self.authenticate_user()
        request = self.client.post(self.produto_url, 
            produto_data, format="json")
        self.assertEqual(request.status_code, 403)

        self.authenticate_superuser()
        request = self.client.post(self.produto_url, 
            produto_data, format="json")
        self.assertEqual(request.status_code, 201)

        request = self.client.put(self.produto_url_detail, 
            produto_data, format="json")
        self.assertEqual(request.status_code, 200)

        request = self.client.patch(self.produto_url_detail, 
            produto_data, format="json")
        self.assertEqual(request.status_code, 200)

        request = self.client.delete(self.produto_url_detail, 
            format="json")
        self.assertEqual(request.status_code, 204)


class PedidoTestCase(AuthenticatedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pedido_url = cls.live_server_url + "/api/pedidos/"

    def setUp(self):
        super().setUp()
        self.usuario = Usuario.objects.get(email=self.user_data['email'])
        pedido_id = Pedido.objects.create(
            usuario=self.usuario,
            endereco='test'
        ).pk

        self.pedido_url_detail = self.pedido_url + f'{pedido_id}/'

    def test_get_pedido(self):
        """User-restricted"""        
        request = self.client.get(self.pedido_url, format="json")
        self.assertEqual(request.status_code, 401)

        self.authenticate_superuser()
        request = self.client.get(self.pedido_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.json(),[])

        self.authenticate_user()
        request = self.client.get(self.pedido_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertNotEqual(request.json(),[])

    def test_non_safe_pedido(self):
        """User-restricted""" 
        
        pedido_data = {
            'usuario':self.usuario.pk,
            'endereco':'test'
        }

        request = self.client.post(self.pedido_url, 
            pedido_data, format="json")
        self.assertEqual(request.status_code, 401)

        self.authenticate_user()
        request = self.client.post(self.pedido_url, 
            pedido_data, format="json")
        self.assertEqual(request.status_code, 201)

        request = self.client.put(self.pedido_url_detail, 
            pedido_data, format="json")
        self.assertEqual(request.status_code, 200)

        request = self.client.patch(self.pedido_url_detail, 
            pedido_data, format="json")
        self.assertEqual(request.status_code, 200)

        request = self.client.delete(self.pedido_url_detail, 
            format="json")
        self.assertEqual(request.status_code, 204)

class PedidoProdutosTestCase(AuthenticatedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.usuario = Usuario.objects.get(email=self.user_data['email'])
        self.pedido = Pedido.objects.create(
            usuario=self.usuario,
            endereco='test'
        )
        pedido_id = self.pedido.pk
        self.produto = Produto.objects.create(
            nome='test',
            descricao='test'
        )
        produto_id = self.produto.pk
        PedidoProduto.objects.create(
            pedido=self.pedido,
            produto=self.produto,
            quantidade=1
        )

        self.produto_url = self.live_server_url + f"/api/pedidos/{pedido_id}/produtos/"
        self.produto_url_detail = self.produto_url + f'{produto_id}/'

    def test_get_produto(self):
        """User-restricted"""        
        request = self.client.get(self.produto_url, format="json")
        self.assertEqual(request.status_code, 401)

        self.authenticate_superuser()
        request = self.client.get(self.produto_url, format="json")
        self.assertEqual(request.status_code, 404)

        self.authenticate_user()
        request = self.client.get(self.produto_url, format="json")
        self.assertEqual(request.status_code, 200)
        self.assertNotEqual(request.json(),[])

    def test_non_safe_produto_url(self):
        """User-restricted""" 
        produto_data = {
            'pedido':self.produto.pk,
            'produto':self.pedido.pk,
            'quantidade':2,
        }

        request = self.client.post(self.produto_url, 
            produto_data, format="json")
        self.assertEqual(request.status_code, 401)

        self.authenticate_user()
        request = self.client.post(self.produto_url, 
            produto_data, format="json")
        self.assertEqual(request.status_code, 201)

        request = self.client.put(self.produto_url_detail, 
            produto_data, format="json")
        self.assertEqual(request.status_code, 200)

        request = self.client.patch(self.produto_url_detail, 
            produto_data, format="json")
        self.assertEqual(request.status_code, 200)

        request = self.client.delete(self.produto_url_detail, 
            format="json")
        self.assertEqual(request.status_code, 204)
