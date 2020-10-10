#!/bin/bash

set -xe

BASE="$(dirname "$0")"
export WORKSPACE="$(cd "${BASE}"/.. && pwd -P)"

cd "${WORKSPACE}"
source bin/exports.sh

pip3 install -U pip setuptools wheel
pip3 install -e .
