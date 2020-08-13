from django.db import models
from django.contrib.auth.models import AbstractUser

from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE

from app.managers import UsuarioManager

# Create your models here.
class Usuario(SafeDeleteModel, AbstractUser):
    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.AutoField(primary_key=True)

    email = models.EmailField(unique=True)
    endereco = models.CharField("Endereço", max_length=200)
    cpf = models.CharField(max_length=30, verbose_name="CPF",)
    rg = models.CharField(max_length=30, verbose_name="RG",)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UsuarioManager()

    def __str__(self):
        return self.email


class Produto(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.AutoField(primary_key=True)
    nome = models.CharField("Nome", max_length=100,)
    descricao = models.CharField("Descrição", max_length=300)

    def __str__(self):
        return str(self.nome)


class Pedido(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "Usuario", verbose_name="Usuário", on_delete=models.CASCADE
    )
    endereco = models.CharField("Endereço", max_length=200)
    feito = models.DateTimeField("Feito em", auto_now_add=True)

    def __str__(self):
        return str(self.feito)


class PedidoProduto(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.AutoField(primary_key=True)
    produto = models.ForeignKey(
        "Produto", verbose_name="Produto", on_delete=models.CASCADE
    )
    pedido = models.ForeignKey(
        "Pedido", verbose_name="Pedido", on_delete=models.CASCADE
    )
    quantidade = models.PositiveIntegerField("Quantidade")

    def __str__(self):
        return f"{self.produto} x{self.quantidade}"
