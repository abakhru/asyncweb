#!/bin/bash

cd ${WORKSPACE}

${VIRUTAL_ENV}/bin/pytest -sv tests/
