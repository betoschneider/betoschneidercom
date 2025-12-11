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
- **Importante:** O app procura `.env` em dois locais (em ordem de prioridade):
  1. `/var/www/.env` (produção em servidor Linux)
  2. `./.env` (desenvolvimento local)

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

Deploy em Produção (/var/www/html)
-----------------------------------

**Estrutura recomendada:**
```
/var/www/
├── .env                      (arquivo .env fora do html, não exposto)
├── html/
│   └── (FastAPI app roda em localhost:8000 via systemd/docker)
└── projetos.db              (opcional: banco fora de html)
```

**Perguntas frequentes:**

1. **É seguro deixar `.env` em `/var/www/html`?**
   - ❌ NÃO. Riscos: exposição via web, erros de configuração, sincronização automática de deploy.
   - ✅ Armazene em `/var/www/.env` (fora de `html`) ou `/etc/linktree/.env`.
   - ✅ Restrinja permissões: `chmod 600 /var/www/.env`

2. **É necessário editar o `index.html` existente?**
   - ❌ NÃO. FastAPI serve automaticamente `static/index.html` na rota `/`.
   - ✅ Configure seu nginx/apache como **reverse proxy** apontando para `http://localhost:8000`.

**Passos para deploy:**

1. Clone o projeto em `/var/www/linktree-app` (fora de `html`):
```bash
cd /var/www
git clone <seu_repo> linktree-app
cd linktree-app
```

2. Copie `.env.production` para `.env` e configure o token:
```bash
cp .env.production .env
nano .env
```

3. Configure nginx/apache como **reverse proxy**:

**Nginx example:**
```nginx
server {
    listen 80;
    server_name seu_dominio.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. Rode o app via Docker ou systemd:

**Docker (recomendado):**
```bash
docker-compose up -d
```

**Systemd (alternativa):**
```bash
# Crie /etc/systemd/system/linktree.service
[Unit]
Description=Linktree FastAPI App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/linktree-app
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/var/www/.env
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

5. Inicie o serviço:
```bash
sudo systemctl start linktree
sudo systemctl enable linktree
```

**Segurança - Boas práticas:**
- ✅ Use `.env` em `/var/www/.env` (fora de html)
- ✅ Configure reverse proxy (nginx/apache)
- ✅ FastAPI serve `static/` automaticamente — nginx não precisa servir arquivos estáticos
- ✅ Em ambiente corporativo, use Docker Secrets ou CI/CD secrets
