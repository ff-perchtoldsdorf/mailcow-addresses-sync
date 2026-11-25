FROM python:3.12-slim

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends postfix \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py docker/sync-loop.sh ./
RUN chmod +x /app/sync-loop.sh
CMD ["/app/sync-loop.sh"]
