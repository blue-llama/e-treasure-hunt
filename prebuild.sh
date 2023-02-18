#!/bin/bash
set -euo pipefail

POETRY="/home/.local/bin/poetry"
if [[ ! -f ${POETRY} ]]; then
  curl -sSL https://install.python-poetry.org | python3
fi
${POETRY} export --output requirements.txt --extras azure
