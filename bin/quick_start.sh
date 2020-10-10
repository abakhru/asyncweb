#!/bin/bash

set -xe

BASE="$(dirname "$0")"
export WORKSPACE="$(cd "${BASE}"/.. && pwd -P)"

cd "${WORKSPACE}"
source bin/exports.sh

if [ ! -d "${VIRTUAL_ENV}" ]; then
  python3 -m venv "${VIRTUAL_ENV}"
fi

"${VIRTUAL_ENV}"/bin/pip install -U pip setuptools wheel
"${VIRTUAL_ENV}"/bin/pip install -e .

# bin/run.sh
