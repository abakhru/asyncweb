#!/bin/bash

set -xe

BASE="$(dirname "$0")"
export WORKSPACE="$(cd "${BASE}"/.. && pwd -P)"

# if not inside docker container
if [ ! -f "/.dockerenv" ]; then
  export VIRTUAL_ENV=${VIRTUAL_ENV:-$WORKSPACE/env}
  if [ ! -d "${VIRTUAL_ENV}" ]; then python3 -m venv "${VIRTUAL_ENV}"; fi
  source "${VIRTUAL_ENV}"/bin/activate
fi

cd "${WORKSPACE}"
source bin/exports.sh

pip3 install --no-cache-dir -U pip setuptools wheel
pip3 install --no-cache-dir -e ".[testing]"
