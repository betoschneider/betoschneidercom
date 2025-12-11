# Linktree-like (FastAPI + JS)

Pequeno projeto que lista projetos (título, descrição, link) e fornece uma página admin para gerenciar os itens.

Requisitos
- Python 3.10+

Instalação (PowerShell)

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Executar

```powershell
$env:ADMIN_TOKEN = "seu_token_aqui"
uvicorn main:app --reload
```

Acesse:
- Página pública: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin (insira o token admin na caixa)

Observações
- O token admin é lido da variável de ambiente `ADMIN_TOKEN` (padrão `changeme`).
- Banco usado: SQLite (arquivo `projects.db` criado na raiz).

Configurando o Token Admin via .env
------------------------------------
Crie um arquivo `.env` na raiz do projeto (ou copie `.env.example`):

```
ADMIN_TOKEN=seu_token_secreto_aqui
```

O arquivo `.env` é automaticamente carregado pelo FastAPI (via `python-dotenv`), e também pelo `docker-compose.yml` via `env_file`.

Docker
------
Você pode rodar a aplicação em contêiner com Docker + docker-compose:

Construir e subir (na pasta do projeto):

```powershell
docker-compose build
docker-compose up -d
```

Por padrão o `ADMIN_TOKEN` é `changeme`. Para definir outro token via variável de ambiente (PowerShell):

```powershell
$env:ADMIN_TOKEN = "seu_token_aqui"
docker-compose up -d --build
```

O banco `projects.db` será persistido no diretório do projeto via volume mapeado.
