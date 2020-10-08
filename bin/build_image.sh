#!/bin/bash
set -xe

export WORKSPACE=${WORKSPACE:-$PWD}
source "${WORKSPACE}/bin/exports.sh"

cd "${WORKSPACE}"
source "${VIRTUAL_ENV}"/bin/activate

env | sort

docker build -t asyncweb -f ./Dockerfile .