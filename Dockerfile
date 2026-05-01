FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY diabolik-archive/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY diabolik-archive/ .

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -sf http://localhost:8080/api/settings/status || exit 1

CMD ["sh", "-c", "cd webapp && python main.py"]
