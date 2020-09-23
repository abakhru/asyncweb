#!/bin/bash

set -xe

export WORKSPACE=${WORKSPACE:-$PWD}
source "${WORKSPACE}"/bin/exports.sh

env|grep VIRTUAL_ENV

cd "${WORKSPACE}"
if [ ! -d "${VIRTUAL_ENV}" ]; then
  python3 -m venv "${VIRTUAL_ENV}"
fi

"${VIRTUAL_ENV}"/bin/pip install -U pip setuptools wheel
"${VIRTUAL_ENV}"/bin/pip install -e .
