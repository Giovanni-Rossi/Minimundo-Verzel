# Imagem da API para o Dokploy (build path: /api). Veja a seção "Deploy no Dokploy" do README.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Em produção a API usa as tabelas do time de banco sem criar nem alterar nada.
    CRIAR_TABELAS=false \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

RUN useradd --create-home api && chown -R api /app
USER api

EXPOSE 8000

# --proxy-headers: o Dokploy fica na frente (Traefik) e repassa o protocolo e o IP do cliente.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
