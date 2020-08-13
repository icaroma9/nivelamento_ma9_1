from django.core.validators import RegexValidator

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from app.models import Usuario, Produto, Pedido, PedidoProduto


class TokenSerializer(TokenObtainPairSerializer):
    username_field = Usuario.EMAIL_FIELD


class UsuarioSerializer(serializers.ModelSerializer):
    cpf = serializers.CharField(
        max_length=30,
        validators=[
            RegexValidator(
                r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$",
                message="Formato esperado: '999.999.999-99'",
            )
        ],
    )

    rg = serializers.CharField(
        max_length=30, validators=[RegexValidator(r"^(\d\.?-?)+$")]
    )

    class Meta:
        model = Usuario
        exclude = ["deleted"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.get("password", None)
        instance = super().create(validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        password = validated_data.get("password")
        if password:
            instance.set_password(password)
            instance.save()
        return instance


class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        exclude = ["deleted"]


class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        exclude = ["deleted"]
        extra_kwargs = {"usuario": {"read_only": True}}

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["usuario"] = user
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        validated_data["usuario"] = self.context["request"].user
        instance = super().update(instance, validated_data)
        return instance


class PedidoProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoProduto
        exclude = ["deleted", "pedido"]

    def create(self, validated_data):
        pedido_pk = self.context["pedidos_pk"]
        pedido = Pedido.objects.get(pk=pedido_pk)
        validated_data["pedido"] = pedido
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        pedido_pk = self.context["pedidos_pk"]
        pedido = Pedido.objects.get(pk=pedido_pk)
        validated_data["pedido"] = pedido
        instance = super().update(instance, validated_data)
        return instance
