# Payment Risk AI — Adaptive 3DS

Motor inteligente de autenticação adaptativa (Adaptive 3DS). O projeto analisa o comportamento
histórico do cliente e os sinais de uma nova tentativa de pagamento para recomendar autenticação
adicional quando identifica uma situação incomum.

Em vez de exigir 3DS indiscriminadamente, o motor considera a combinação dos sinais disponíveis.
Uma tentativa isolada pode ser legítima, mas diversos desvios simultâneos aumentam o risco e podem
resultar na recomendação de autenticação adicional.

Exemplo de mudança comportamental:

| Informação | Histórico do cliente | Nova tentativa |
| --- | --- | --- |
| Valor | R$ 100–300 | R$ 2.500 |
| Horário | 12h–21h | 03h |
| Dispositivo | iPhone A | Android B |
| Localização aproximada | Florianópolis | São Paulo |
| Tentativas recentes | 1–2 | 8 |
| Recusas recentes | 0 | 6 |

O serviço é construído com FastAPI e Clean Architecture, utilizando PostgreSQL e Redis como base
para a evolução das regras comportamentais e da decisão de Adaptive 3DS.

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
- Registro autenticado de transação: `POST /api/v1/transactions`
- Swagger: <http://localhost:8000/docs>

O código em `app/` é montado no container e o Uvicorn executa com reload automático.

### Autenticação e registro de transação

Todos os endpoints sob `/api/v1` exigem uma chave no header `X-API-Key`. Somente o hash SHA-256 da
chave é armazenado em `api_keys.key_hash`; a chave também precisa pertencer a uma empresa ativa e
não pode estar revogada ou expirada. `/health`, `/ready` e a documentação permanecem públicos.

```bash
curl --request POST http://localhost:8000/api/v1/transactions \
  --header 'Content-Type: application/json' \
  --header 'X-API-Key: sua-chave' \
  --data '{
    "external_id": "txn_100001",
    "customer_id": "customer_123",
    "amount": "250.00",
    "currency": "BRL",
    "payment_method": "credit_card",
    "status": "pending",
    "ip_address": "189.45.120.10",
    "device_id": "device_abc123",
    "card_bin": "411111",
    "card_last_four": "1234"
  }'
```

Uma criação válida retorna `201`. Chaves ausentes ou inválidas retornam `401`; repetir o mesmo
`external_id` para a mesma empresa retorna `409`.

Para testar apenas a autenticação:

```bash
curl http://localhost:8000/api/v1/risk/test \
  --header 'X-API-Key: sua-chave'
```

### Cadastro manual de API Key

A forma recomendada é usar o comando administrativo do container. Consulte primeiro o UUID da
empresa e então gere a credencial:

```bash
docker compose exec postgres psql -U payment_risk -d payment_risk \
  -c "SELECT id, name, is_active FROM companies;"

docker compose exec api python -m app.cli.create_api_key \
  --company-id UUID_DA_EMPRESA \
  --name "Postman local"
```

O comando salva somente o hash SHA-256 no banco e mostra a chave original uma única vez. Copie a
chave exibida e guarde-a em local seguro.

Se precisar gerar e inserir os valores manualmente, use o procedimento abaixo.

Gere uma chave e seu hash localmente. A saída `API_KEY` é mostrada uma única vez e deve ser
guardada em local seguro; somente `KEY_HASH` e `KEY_PREFIX` vão para o banco.

```bash
python3 -c "import hashlib, secrets; key='prk_'+secrets.token_urlsafe(32); print('API_KEY='+key); print('KEY_PREFIX='+key[:16]); print('KEY_HASH='+hashlib.sha256(key.encode()).hexdigest())"
```

Cadastre os valores gerados para uma empresa existente, substituindo os placeholders:

```bash
docker compose exec postgres psql -U payment_risk -d payment_risk -c "
INSERT INTO api_keys (id, company_id, name, key_prefix, key_hash)
VALUES (
  gen_random_uuid(),
  'UUID_DA_EMPRESA',
  'Postman local',
  'KEY_PREFIX_GERADO',
  'KEY_HASH_GERADO'
);"
```

No Postman, selecione a aba **Headers** e adicione `X-API-Key` com o valor completo de `API_KEY`.
Não envie `KEY_HASH`: o serviço calcula o SHA-256 da chave recebida antes de consultar o banco.

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
