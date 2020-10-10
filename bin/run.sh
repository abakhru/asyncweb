#!/bin/bash
set -xe

BASE="$(dirname "$0")"
export WORKSPACE="$(cd "${BASE}"/.. && pwd -P)"

cd "${WORKSPACE}"
source bin/exports.sh
source "${VIRTUAL_ENV}"/bin/activate

env | sort

"${VIRTUAL_ENV}"/bin/python -m uvicorn src.server:app --reload --workers 1 --host 0.0.0.0 --port 8000
