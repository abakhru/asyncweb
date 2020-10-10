#!/bin/bash
set -xe

BASE="$(dirname "$0")"
export WORKSPACE="$(cd "${BASE}"/.. && pwd -P)"

cd "${WORKSPACE}"
source bin/exports.sh

env | sort

python3 -m uvicorn src.server:app --reload --workers 1 --host 0.0.0.0 --port 8000