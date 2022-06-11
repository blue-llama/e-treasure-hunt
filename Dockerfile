FROM python:3.9 AS exporter

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY pyproject.toml poetry.lock /
RUN /root/.local/bin/poetry export -f requirements.txt -o requirements.txt

FROM python:3.9

RUN apt-get update && \
    apt-get install --yes --no-install-recommends unixodbc-dev && \
    rm -fr /var/lib/apt/lists/*

COPY --from=exporter /requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

WORKDIR /usr/src/app
EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
