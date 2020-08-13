# Nivelamento 1

Projeto de nivelamento para o cargo de Desenvolvedor Python (DRF).

## Tabela
Usuário (subclasse de django.config.auth.models.AbstractUser)
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
- Os endpoints de produtos aceitam apenas o verbo GET para qualquer solicitação (exceto para solicitações de superusuários)
- O verbo GET em api/usuarios/ só pode ser usado por superusuários
- O verbo POST em api/usuarios/ pode ser usado por todos
- Todos os outros endpoints não podem ser acessados sem autenticação
- Autenticação é feita com JWT, com email e senha
- A manipulação dos dados nos endpoints de pedidos é restrita para os pedidos específicos do usuário autenticado
- Remoções são feitas de maneira lógica, com o armazenamento da data e hora (datetime) da remoção. 

## Como executar
1. Clonar repositório
2. Configurar ambiente virtual a partir do arquivo Pipfile (pipenv) ou requirements.txt
3. Configurar variáveis de ambiente em um arquivo .env na raiz do projeto:
- SECRET_KEY: chave do Django
- DEBUG: flag para ambiente de desenvolvimento
- DB_ENGINE: engine do banco de dados para ser carregada pelo Django
- DB_NAME: nome do banco de dados
- DB_USER: usuário do banco de dados
- DB_PASSWORD: senha do usuário do banco de dados
- DB_HOST: host do serviço de banco de dados
- DB_PORT: porta do serviço de banco de dados
4. Criar migrações `python manage.py makemigrations app`
5. Executar migrações `python manage.py migrate`
6. Criar um superusuário `python manage.py createsuperuser`
7. Executar servidor `python manage.py runserver`

### Testes
Executar servidor `python manage.py test`
