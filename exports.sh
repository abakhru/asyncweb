export PYTHONIOENCODING=utf-8
export PYTHONUNBUFFERED=1
export POSTGRES_USER="amit"
export POSTGRES_PASSWORD="amit"
export POSTGRES_DB="asyncweb"
export POSTGRES_HOST="db"
#export POSTGRES_HOST=${POSTGRES_HOST:-"0.0.0.0"}
export DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DB}"
export WORKSPACE=${WORKSPACE:-$PWD}
export PYTHONPATH=${WORKSPACE}
export VIRTUAL_ENV=${VIRTUAL_ENV:-WORKSPACE/env}
