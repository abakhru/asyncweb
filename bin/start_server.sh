#!/bin/bash
set -xe

BASE="$(dirname "$0")"
export WORKSPACE="$(cd "${BASE}"/.. && pwd -P)"
source bin/exports.sh
docker-compose up -d