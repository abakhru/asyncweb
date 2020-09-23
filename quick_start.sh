#!/bin/bash

set -xe
export WORKSPACE=${PWD}
export PYTHONPATH=${WORKSPACE}
export PYTHONIOENCODING=utf-8
export PYTHONUNBUFFERED=1
export VIRTUAL_ENV=${VIRTUAL_ENV:-$WORKSPACE/env}
source "${WORKSPACE}"/.env
export DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db/${POSTGRES_DB}

cd "${WORKSPACE}"
if [ ! -d "${VIRTUAL_ENV}" ]; then
  python3 -m venv "${VIRTUAL_ENV}"
fi

"${VIRTUAL_ENV}"/bin/pip install -U pip setuptools wheel
"${VIRTUAL_ENV}"/bin/pip install -e .
