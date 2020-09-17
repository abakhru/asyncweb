#!/bin/bash
set -xe

export VIRTUAL_ENV=${VIRTUAL_ENV:-$WORKDIR/env}
env | sort

cd "${WORKDIR}"
source "${VIRTUAL_ENV}"/bin/activate

"${VIRTUAL_ENV}"/bin/python -m uvicorn src.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
