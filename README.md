# Payment Risk AI

Base de um microsserviço FastAPI para futuras funcionalidades de risco de pagamentos. O projeto
inclui health checks, conexões de infraestrutura, estrutura em camadas e persistência inicial de
empresas, chaves de API e transações. As regras de análise de risco ainda não estão implementadas.

## Requisitos

- Docker com Docker Compose v2
- Portas `8000` e `5432` livres no host

## Configuração e execução

Crie o arquivo local de ambiente e ajuste a senha antes do primeiro uso:

```bash
cp .env.example .env
docker compose up -d --build
```

O arquivo `.env` não é versionado. `DATABASE_URL` deve usar os mesmos usuário, senha e banco das
variáveis `POSTGRES_*`. Dentro do Compose, os hosts são `postgres` e `redis`.

Comandos habituais:

```bash
docker compose logs -f api          # acompanhar logs
docker compose stop                 # parar sem remover containers
docker compose down                 # parar e remover containers/rede
docker compose down -v              # também apaga os dados persistidos
```

PostgreSQL e Redis usam volumes nomeados, portanto os dados sobrevivem a `stop`, reinícios e
`down` sem a opção `-v`.

## Endpoints

- Health: <http://localhost:8000/health>
- Readiness de PostgreSQL e Redis: <http://localhost:8000/ready>
- Swagger: <http://localhost:8000/docs>

O código em `app/` é montado no container e o Uvicorn executa com reload automático.

## Banco e migrations

Execute migrations dentro da API:

```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic revision --autogenerate -m "descricao"
```

Para acessar o PostgreSQL pelo host, use `127.0.0.1:5432` e as credenciais do `.env`. Exemplo com
`psql` instalado localmente:

```bash
psql -h 127.0.0.1 -p 5432 -U payment_risk -d payment_risk
```

Redis não publica porta no host e fica acessível somente aos serviços da rede do Compose.

## Testes e qualidade

```bash
docker compose exec api pytest
docker compose exec api ruff check .
```

## Dependências

As versões são controladas no `pyproject.toml`. Para adicionar uma dependência, inclua-a em
`dependencies` (ou em `project.optional-dependencies.dev` para ferramentas), fixe uma versão
compatível e reconstrua a imagem:

```bash
docker compose build --no-cache api
docker compose up -d
```

## Estrutura

- `app/api`: apresentação HTTP, versões de rotas, schemas e dependências FastAPI.
- `app/application`: casos de uso e DTOs futuros.
- `app/domain`: entidades, value objects, serviços e contratos do domínio futuros.
- `app/infrastructure`: SQLAlchemy, Redis, repositórios e integrações de ML futuras.
- `app/core`: configuração e logging transversais da aplicação.
- `alembic`: configuração e versões das migrations.
- `tests`: testes automatizados.
