FROM python:3.10-slim

WORKDIR /app

# Устанавливаем только самые необходимые системные пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ /app/bot/

WORKDIR /app/bot

CMD ["python", "main.py"]