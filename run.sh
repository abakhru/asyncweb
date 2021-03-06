#!/bin/bash
set -xe

export WORKSPACE=${WORKSPACE:-$PWD}
source "${WORKSPACE}/exports.sh"

cd "${WORKDIR}"
source "${VIRTUAL_ENV}"/bin/activate

env | sort

"${VIRTUAL_ENV}"/bin/python -m uvicorn src.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
