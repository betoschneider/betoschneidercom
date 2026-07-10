FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . /app

# Cria usuário não-root
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app

# Entrypoint (roda como root para ajustar permissões, depois desce para appuser)
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
