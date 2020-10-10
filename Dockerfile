FROM python:3.8-slim-buster
LABEL maintainer="amit <bakhru@me.com>"

# set environment variables
ARG UID=1000
ARG WORKDIR=/app
ENV USER=amit PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DEBIAN_FRONTEND=noninteractive

# set work directory
WORKDIR ${WORKDIR}

# create a non-root default user
RUN useradd -d /home/${USER} -u ${UID} -ms /bin/bash ${USER} && \
    echo "${USER}:${USER}" | chpasswd && \
    chown -R "${USER}:${USER}" "${HOME}" && \
    # remove the sudo permissions when in production
    adduser ${USER} sudo && \
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
    bin/quick_start.sh

EXPOSE 8000

CMD ["/app/bin/run.sh"]
