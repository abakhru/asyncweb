#!/bin/bash
set -xe

export WORKSPACE=${WORKSPACE:-$PWD}
source "${WORKSPACE}/exports.sh"
export VIRTUAL_ENV=${VIRTUAL_ENV:-$WORKSPACE/env}

cd "${WORKSPACE}"
docker build -t asyncweb -f Dockerfile .
docker-compose up -d