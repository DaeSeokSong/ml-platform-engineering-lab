FROM python:3.11-bookworm

ENV HOME=/tmp \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.lock.txt /app/requirements.lock.txt

RUN python -m pip install --no-cache-dir \
      -r /app/requirements.lock.txt \
    && python -m pip check

USER 1000:1000
