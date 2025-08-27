FROM python:3.13-alpine3.21 AS build

ENV UV_PROJECT_ENVIRONMENT=/ve \
    UV_COMPILE_BYTECODE=1      \
    UV_LINK_MODE=copy          \
    UV_PYTHON_DOWNLOADS=never

RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev \
        openssl-dev \
        libxml2-dev \
        libxslt-dev \
        libjpeg-turbo-dev \
        libpng-dev \
    && \
    # Set the container's timezone to Los Angeles time.
    ln -snf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime && \
    rm -r /usr/share/zoneinfo/Africa && \
    rm -r /usr/share/zoneinfo/Antarctica && \
    rm -r /usr/share/zoneinfo/Arctic && \
    rm -r /usr/share/zoneinfo/Asia && \
    rm -r /usr/share/zoneinfo/Atlantic && \
    rm -r /usr/share/zoneinfo/Australia && \
    rm -r /usr/share/zoneinfo/Europe  && \
    rm -r /usr/share/zoneinfo/Indian && \
    rm -r /usr/share/zoneinfo/Mexico && \
    rm -r /usr/share/zoneinfo/Pacific && \
    rm -r /usr/share/zoneinfo/Chile && \
    rm -r /usr/share/zoneinfo/Canada && \
    echo 'America/Los_Angeles' > /etc/timezone && \
    pip3 install --no-cache-dir uv

RUN --mount=type=cache,target=/uv-cache \
    --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv --cache-dir=/uv-cache sync --frozen --no-install-project

FROM python:3.13-alpine3.21

ENV HISTCONTROL=ignorespace:ignoredups  \
    IPYTHONDIR=/etc/ipython             \
    # Add the venv's binaries, and the /app folder, to the PATH.
    PATH=/ve/bin:/app:$PATH             \
    PYCURL_SSL_LIBRARY=nss              \
    SHELL_PLUS=ipython                  \
    # Setting this env var is all you need to do to set the timezone in Debian.
    TZ=America/Los_Angeles              \
    # Tell uv where the venv is, and to always copy instead of hardlink, which is needed for a mounted uv cache.
    UV_PROJECT_ENVIRONMENT=/ve          \
    UV_LINK_MODE=copy                   \
    # Tell python which venv to use.
    VIRTUAL_ENV=/ve

RUN apk update && \
    apk upgrade && \
    apk add --no-cache nmap curl && \
    # Set the container's timezone to Los Angeles time.
    ln -snf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime && \
    rm -r /usr/share/zoneinfo/Africa && \
    rm -r /usr/share/zoneinfo/Antarctica && \
    rm -r /usr/share/zoneinfo/Arctic && \
    rm -r /usr/share/zoneinfo/Asia && \
    rm -r /usr/share/zoneinfo/Atlantic && \
    rm -r /usr/share/zoneinfo/Australia && \
    rm -r /usr/share/zoneinfo/Europe  && \
    rm -r /usr/share/zoneinfo/Indian && \
    rm -r /usr/share/zoneinfo/Mexico && \
    rm -r /usr/share/zoneinfo/Pacific && \
    rm -r /usr/share/zoneinfo/Chile && \
    rm -r /usr/share/zoneinfo/Canada && \
    echo 'America/Los_Angeles' > /etc/timezone && \
    apk cache purge && \
    # Add the user under which we will run.
    adduser -H -D sidecar && \
    # Make our virtualenv
    pip3 install --no-cache-dir uv

COPY --from=build --chown=app:app /ve /ve
ENV PATH=/ve/bin:/usr/local/bin:$PATH
ENV PYTHONPATH=/app

COPY . /app
WORKDIR /app


RUN --mount=type=cache,target=/uv-cache \
    uv --cache-dir=/uv-cache sync --frozen


USER sidecar

CMD ["/ve/bin/sidecar", "run"]
