#!/bin/bash
set -xe

export WORKSPACE=${WORKSPACE:-$PWD}
source "${WORKSPACE}/bin/exports.sh"
export VIRTUAL_ENV=${HOME}/env

cd "${WORKSPACE}"
source "${VIRTUAL_ENV}"/bin/activate

env | sort

"${VIRTUAL_ENV}"/bin/python -m uvicorn app.app:app --reload --workers 1 --host 0.0.0.0 --port 8000
