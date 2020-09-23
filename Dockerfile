FROM python:3.8-slim-buster
LABEL maintainer="amit <bakhru@me.com>"

# set environment variables
ENV USER=amit PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 WORKDIR=/app DEBIAN_FRONTEND=noninteractive
ARG UID=1000

# set work directory
WORKDIR ${WORKDIR}

# create a non-root default user
RUN useradd -d /home/${USER} -u ${UID} -ms /bin/bash ${USER} && \
    echo "${USER}:${USER}" | chpasswd && adduser ${USER} sudo && \
    chown -R "${USER}:${USER}" "${HOME}" && \
    echo "${USER} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# install dependencies
RUN set -eux && \
    apt update && \
    apt full-upgrade -y && \
    apt install -y --no-install-recommends \
    curl \
    gcc \
    libc-dev \
    libffi-dev \
    musl-dev \
    libpq-dev && \
    apt install -y sudo --option=Dpkg::Options::=--force-confdef && \
    apt clean && apt autoremove -y && \
    mkdir -p ${WORKDIR} && rm -rf /home/${USER}/.cache/pip && \
    chown -R ${USER}:${USER} ${WORKDIR} && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

USER ${USER}
COPY --chown=amit:amit . ${WORKDIR}/
RUN echo "alias l='ls -larth'" >> /home/${USER}/.bashrc && \
    ./quick_start.sh

EXPOSE 8000

CMD ["bash", "-c", "python", "-m uvicorn src.main:app --reload --workers 1 --host 0.0.0.0 --port 8000"]
