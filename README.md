# Cupido do Bem

Sistema de gestão de estoque, equipes e vendas com consignação. Flask + SQLAlchemy,
SQLite em desenvolvimento e PostgreSQL em produção (Render).

## Rodando localmente

```powershell
python -m venv venv
.\venv\Scripts\pip.exe install -r requirements-dev.txt

# aplica as migrações (cria o banco SQLite em instance/)
$env:FLASK_APP = "wsgi.py"
.\venv\Scripts\flask.exe db upgrade

# popula dados de demonstração (usuários, equipes, produtos) com senhas aleatórias
.\venv\Scripts\python.exe scripts\seed.py
# credenciais geradas em seed_credentials_LOCAL.txt (não versionado)

.\venv\Scripts\python.exe -m flask run
```

Acesse http://127.0.0.1:5000.

## Testes

```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

## Estrutura

- `app/` — blueprints por módulo (auth, admin, produtos, equipes, precificacao,
  consignacoes, vendas, caixa, relatorios, main), modelos em `app/models/`.
- `app/utils.py` — lógica compartilhada de maior risco: cálculo de preço, registro
  de movimentação de estoque (com auditoria), baixa atômica de consignação.
- `migrations/` — migrações Alembic (Flask-Migrate).
- `scripts/seed.py` — dados de demonstração.

## Deploy (Render)

1. Crie uma conta em https://render.com (gratuita, sem cartão).
2. Suba este repositório para o GitHub.
3. No Render: **New +** → **Blueprint**, aponte para o repositório — o
   `render.yaml` já descreve o Web Service e o banco PostgreSQL free tier.
4. O Render provisiona `DATABASE_URL` e `SECRET_KEY` automaticamente
   (ver `render.yaml`). O comando de start já roda `flask db upgrade`
   antes de subir o Gunicorn.
5. Depois do primeiro deploy, rode o script de seed uma vez via Render Shell
   (ou crie os usuários reais manualmente pelo painel de administração) e
   troque as senhas padrão.

## Segurança

- CSRF (Flask-WTF) ativo em todos os formulários.
- Rate limiting (Flask-Limiter) no login.
- Sessão expira em 2h de inatividade.
- Auditoria: toda movimentação de estoque e todo evento de login
  falho/permissão negada fica registrado (`Movimentacao`, `LogSeguranca`).
