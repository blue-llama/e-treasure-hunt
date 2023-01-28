FROM python:3.11-slim AS builder

RUN apt-get update && \
    apt-get install \
      --yes \
      --no-install-recommends \
      curl && \
    curl \
      --silent \
      --show-error \
      --location \
      --output install-poetry.py \
      https://install.python-poetry.org && \
    python3 install-poetry.py && \
    python3 -m venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml poetry.lock /

RUN /root/.local/bin/poetry install --only=main

FROM python:3.11-slim

COPY --from=builder /opt/venv /opt/venv

WORKDIR /usr/src/app
EXPOSE 8000
ENTRYPOINT ["/opt/venv/bin/python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
