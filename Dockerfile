FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY main.py .
COPY data ./data

RUN useradd --create-home --shell /usr/sbin/nologin hcp \
    && chown -R hcp:hcp /app

USER hcp

CMD ["python", "main.py"]
