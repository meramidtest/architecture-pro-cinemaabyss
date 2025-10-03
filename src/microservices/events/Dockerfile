FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
  && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8082

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/start.sh"]
