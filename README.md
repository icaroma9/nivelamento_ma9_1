# Nivelamento 1

Projeto de nivelamento para o cargo de Desenvolvedor Python (DRF).

## Tabela
Usuário (Subclasse de django.config.auth.models.AbstractUser)
- endereço (texto)
- rg (texto, checa com o regex "^\d{3}\.\d{3}\.\d{3}\-\d{2}$")
- cpf (texto, checa com o regex "^(\d\.?-?)+$")

Produto
- nome (texto)
- descrição (texto)

Pedido
- usuário (chave estrangeira)
- endereço (texto)
- feito (data e hora, adicionado automaticamente)

PedidoProduto
- produto (chave estrangeira)
- pedido (chave estrangeira)
- quantidade (inteiro positivo)

## Endpoints
- api/token/     
- api/token/refresh/  
- api/usuarios/
- api/usuarios/id/
- api/produtos/  
- api/produtos/id/
- api/pedidos/
- api/pedidos/id/
- api/pedidos/id/produtos/
- api/pedidos/id/produtos/id/

## Observações
- Os endpoints de token não requerem autenticação
- Todos os outros endpoints não podem ser acessados sem autenticação
- Autenticação é feita com JWT, com email e senha
- A manipulação dos dados nos endpoints de pedidos é restrita para os pedidos específicos do usuário autenticado
- O pylint pode ser executado na raiz do projeto com o comando `pylint project`
- Remoções são feitas de maneira lógica, com o armazenamento da data e hora (datetime) da remoção. 

## Como executar
1. Configurar ambiente virtual a partir do arquivo Pipfile (pipenv) ou requirements.txt
2. Executar migrações `project/manage.py migrate`
3. Criar um super usuário `project/manage.py createsuperuser`
4. Executar servidor `project/manage.py runserver`
