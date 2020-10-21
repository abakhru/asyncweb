#!/bin/bash
set -xe

BASE="$(dirname "$0")"
export WORKSPACE="$(cd "${BASE}"/.. && pwd -P)"

# if not inside docker container
if [ ! -f "/.dockerenv" ]; then
  export POSTGRES_HOST="0.0.0.0"
  docker-compose -f ./docker-compose.yml up -d db
fi
source bin/exports.sh

env | sort

cd "${WORKSPACE}"
python3 -m uvicorn src.server:app --reload --workers 1 --host 0.0.0.0 --port 8000