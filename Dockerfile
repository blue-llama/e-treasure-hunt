FROM python:3.9-slim

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY pyproject.toml poetry.lock /

RUN apt-get update && \
    apt-get install \
      --yes \
      --no-install-recommends \
      curl \
      g++ \
      unixodbc \
      unixodbc-dev && \
    rm -fr /var/lib/apt/lists/* && \
    curl \
      --silent \
      --show-error \
      --location \
      --output install-poetry.py \
      https://install.python-poetry.org && \
    python3 install-poetry.py && \
    POETRY_VIRTUALENVS_CREATE=false /root/.local/bin/poetry export \
      -f requirements.txt \
      -o requirements.txt && \
    python3 install-poetry.py --uninstall && \
    rm install-poetry.py && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt && \
    apt-get purge \
      --yes \
      --auto-remove \
      curl \
      g++  \
      unixodbc-dev && \
    rm -fr /root/.cache && \
    apt-get clean

WORKDIR /usr/src/app
EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
