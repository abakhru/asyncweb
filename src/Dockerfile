FROM python:3.8-slim-buster
LABEL maintainer="amit <bakhru@me.com>"

# set environment variables
ENV USER=amit PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 WORKDIR=/usr/src/app

# set work directory
WORKDIR ${WORKDIR}

# create a non-root default user
RUN useradd -m -d /home/${USER} -s /bin/bash ${USER} && \
    echo "${USER}:${USER}" | chpasswd && \
    adduser ${USER} sudo

# install dependencies
RUN set -eux && \
    apt update && \
    apt full-upgrade -y && \
    apt autoremove -y && \
    apt install -y --no-install-recommends \
    sudo curl gcc libc-dev libffi-dev musl-dev python3-dev libpq-dev && \
    apt clean && apt autoremove -y && rm -rf /var/lib/apt/lists/* && \
    mkdir -p ${WORKDIR} && rm -rf /home/${USER}/.cache/pip && \
    chown -R ${USER}:${USER} ${WORKDIR} && \
    python3 -m pip install -U pip setuptools poetry

USER ${USER}
COPY . ${WORKDIR}

USER ${USER}
RUN poetry install && \
    echo "alias l='ls -larth'" >> /home/${USER}/.bashrc && \
    echo 'source "$(poetry env info -p)/bin/activate"' >> /home/${USER}/.bashrc

CMD ["bash", "-c", "python", "-m uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000"]
