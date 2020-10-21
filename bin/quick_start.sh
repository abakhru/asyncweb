#!/bin/bash

set -xe

BASE="$(dirname "$0")"
export WORKSPACE="$(cd "${BASE}"/.. && pwd -P)"

# todo: if .dockerenv file is not present

cd "${WORKSPACE}"
source bin/exports.sh


pip3 install --no-cache-dir -U pip setuptools wheel
pip3 install --no-cache-dir -e .
