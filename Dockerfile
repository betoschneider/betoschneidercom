FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . /app

# Cria usuário não-root (opcional)
RUN useradd -m appuser || true
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
