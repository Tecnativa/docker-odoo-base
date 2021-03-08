FROM python:3.6-slim-buster AS base

EXPOSE 8069 8072

ARG GEOIP_UPDATER_VERSION=4.1.5
ARG MQT=https://github.com/OCA/maintainer-quality-tools.git
ARG WKHTMLTOPDF_VERSION=0.12.5
ARG WKHTMLTOPDF_CHECKSUM='1140b0ab02aa6e17346af2f14ed0de807376de475ba90e1db3975f112fbd20bb'
ENV DB_FILTER=.* \
    DEPTH_DEFAULT=1 \
    DEPTH_MERGE=100 \
    EMAIL=https://hub.docker.com/r/tecnativa/odoo \
    GEOIP_ACCOUNT_ID="" \
    GEOIP_LICENSE_KEY="" \
    GIT_AUTHOR_NAME=docker-odoo \
    INITIAL_LANG="" \
    LC_ALL=C.UTF-8 \
    LIST_DB=false \
    NODE_PATH=/usr/local/lib/node_modules:/usr/lib/node_modules \
    OPENERP_SERVER=/opt/odoo/auto/odoo.conf \
    PATH="/home/odoo/.local/bin:$PATH" \
    PIP_NO_CACHE_DIR=0 \
    PTVSD_ARGS="--host 0.0.0.0 --port 6899 --wait --multiprocess" \
    PTVSD_ENABLE=0 \
    DEBUGPY_ARGS="--listen 0.0.0.0:6899 --wait-for-client" \
    DEBUGPY_ENABLE=0 \
    PUDB_RDB_HOST=0.0.0.0 \
    PUDB_RDB_PORT=6899 \
    PYTHONOPTIMIZE=1 \
    UNACCENT=true \
    WAIT_DB=true \
    WDB_NO_BROWSER_AUTO_OPEN=True \
    WDB_SOCKET_SERVER=wdb \
    WDB_WEB_PORT=1984 \
    WDB_WEB_SERVER=localhost

# Other requirements and recommendations
# See https://github.com/$ODOO_SOURCE/blob/$ODOO_VERSION/debian/control
RUN apt-get -qq update \
    && apt-get install -yqq --no-install-recommends \
        curl \
    && curl -SLo wkhtmltox.deb https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/${WKHTMLTOPDF_VERSION}/wkhtmltox_${WKHTMLTOPDF_VERSION}-1.stretch_amd64.deb \
    && echo "${WKHTMLTOPDF_CHECKSUM}  wkhtmltox.deb" | sha256sum -c - \
    && apt-get install -yqq --no-install-recommends \
        ./wkhtmltox.deb \
        chromium \
        ffmpeg \
        fonts-liberation2 \
        gettext \
        git \
        gnupg2 \
        locales-all \
        nano \
        npm \
        openssh-client \
        telnet \
        vim \
        zlibc \
    && echo 'deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main' >> /etc/apt/sources.list.d/postgresql.list \
    && curl -SL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install -yqq --no-install-recommends \
    && curl --silent -L --output geoipupdate_${GEOIP_UPDATER_VERSION}_linux_amd64.deb https://github.com/maxmind/geoipupdate/releases/download/v${GEOIP_UPDATER_VERSION}/geoipupdate_${GEOIP_UPDATER_VERSION}_linux_amd64.deb \
    && dpkg -i geoipupdate_${GEOIP_UPDATER_VERSION}_linux_amd64.deb \
    && rm geoipupdate_${GEOIP_UPDATER_VERSION}_linux_amd64.deb \
    && apt-get autopurge -yqq \
    && rm -Rf wkhtmltox.deb /var/lib/apt/lists/* /tmp/* \
    && sync

WORKDIR /opt/odoo
COPY bin/* /usr/local/bin/
COPY lib/doodbalib /usr/local/lib/python3.6/site-packages/doodbalib
COPY build.d common/build.d
COPY conf.d common/conf.d
COPY entrypoint.d common/entrypoint.d
RUN mkdir -p auto/addons auto/geoip custom/src/private \
    && ln /usr/local/bin/direxec common/entrypoint \
    && ln /usr/local/bin/direxec common/build \
    && chmod -R a+rx common/entrypoint* common/build* /usr/local/bin \
    && chmod -R a+rX /usr/local/lib/python3.6/site-packages/doodbalib \
    && mv /etc/GeoIP.conf /opt/odoo/auto/geoip/GeoIP.conf \
    && ln -s /opt/odoo/auto/geoip/GeoIP.conf /etc/GeoIP.conf \
    && sed -i 's/.*DatabaseDirectory .*$/DatabaseDirectory \/opt\/odoo\/auto\/geoip\//g' /opt/odoo/auto/geoip/GeoIP.conf \
    && sync

# Doodba-QA dependencies in a separate virtualenv
COPY qa /qa
RUN python -m venv --system-site-packages /qa/venv \
    && . /qa/venv/bin/activate \
    && pip install \
        click \
        coverage \
        flake8 \
        pylint-odoo \
        six \
    && npm install --loglevel error --prefix /qa eslint \
    && deactivate \
    && mkdir -p /qa/artifacts \
    && git clone --depth 1 $MQT /qa/mqt

ARG ODOO_SOURCE=OCA/OCB
ARG ODOO_VERSION=13.0
ENV ODOO_VERSION="$ODOO_VERSION"

# Install Odoo hard & soft dependencies, and Doodba utilities
RUN build_deps=" \
        build-essential \
        libfreetype6-dev \
        libfribidi-dev \
        libghc-zlib-dev \
        libharfbuzz-dev \
        libjpeg-dev \
        liblcms2-dev \
        libldap2-dev \
        libopenjp2-7-dev \
        libpq-dev \
        libsasl2-dev \
        libtiff5-dev \
        libwebp-dev \
        libxml2-dev \
        libxslt-dev \
        tcl-dev \
        tk-dev \
        zlib1g-dev \
    " \
    && apt-get update \
    && apt-get install -yqq --no-install-recommends $build_deps \
    && pip install \
        -r https://raw.githubusercontent.com/$ODOO_SOURCE/$ODOO_VERSION/requirements.txt \
        'websocket-client~=0.56' \
        astor \
        git-aggregator \
        # Install fix from https://github.com/acsone/click-odoo-contrib/pull/93
        git+https://github.com/Tecnativa/click-odoo-contrib.git@fix-active-modules-hashing \
        "pg_activity<=2.0.3" \
        phonenumbers \
        plumbum \
        ptvsd \
        debugpy \
        pydevd-odoo \
        pudb \
        watchdog \
        wdb \
        geoip2 \
        inotify \
    && (python3 -m compileall -q /usr/local/lib/python3.6/ || true) \
    && apt-get purge -yqq $build_deps \
    && apt-get autopurge -yqq \
    && rm -Rf /var/lib/apt/lists/* /tmp/*

# Metadata
ARG VCS_REF
ARG BUILD_DATE
ARG VERSION
LABEL org.label-schema.schema-version="$VERSION" \
      org.label-schema.vendor=Tecnativa \
      org.label-schema.license=Apache-2.0 \
      org.label-schema.build-date="$BUILD_DATE" \
      org.label-schema.vcs-ref="$VCS_REF" \
      org.label-schema.vcs-url="https://github.com/Tecnativa/doodba"

# Onbuild version, with all the magic
FROM base AS onbuild

# Enable setting custom uids for odoo user during build of scaffolds
ONBUILD ARG UID=1000
ONBUILD ARG GID=1000

# Enable Odoo user and filestore
ONBUILD RUN groupadd -g $GID odoo -o \
    && useradd -l -md /home/odoo -s /bin/false -u $UID -g $GID odoo \
    && mkdir -p /var/lib/odoo \
    && chown -R odoo:odoo /var/lib/odoo /qa/artifacts \
    && chmod a=rwX /qa/artifacts \
    && sync

# Subimage triggers
ONBUILD ENTRYPOINT ["/opt/odoo/common/entrypoint"]
ONBUILD CMD ["/usr/local/bin/odoo"]
ONBUILD ARG AGGREGATE=true
ONBUILD ARG DEFAULT_REPO_PATTERN="https://github.com/OCA/{}.git"
ONBUILD ARG DEFAULT_REPO_PATTERN_ODOO="https://github.com/OCA/OCB.git"
ONBUILD ARG DEPTH_DEFAULT=1
ONBUILD ARG DEPTH_MERGE=100
ONBUILD ARG CLEAN=true
ONBUILD ARG COMPILE=true
ONBUILD ARG FONT_MONO="Liberation Mono"
ONBUILD ARG FONT_SANS="Liberation Sans"
ONBUILD ARG FONT_SERIF="Liberation Serif"
ONBUILD ARG PIP_INSTALL_ODOO=true
ONBUILD ARG ADMIN_PASSWORD=admin
ONBUILD ARG SMTP_SERVER=smtp
ONBUILD ARG SMTP_PORT=25
ONBUILD ARG SMTP_USER=false
ONBUILD ARG SMTP_PASSWORD=false
ONBUILD ARG SMTP_SSL=false
ONBUILD ARG EMAIL_FROM=""
ONBUILD ARG PROXY_MODE=false
ONBUILD ARG WITHOUT_DEMO=all
ONBUILD ARG PGUSER=odoo
ONBUILD ARG PGPASSWORD=odoopassword
ONBUILD ARG PGHOST=db
ONBUILD ARG PGPORT=5432
ONBUILD ARG PGDATABASE=prod

# Config variables
ONBUILD ENV ADMIN_PASSWORD="$ADMIN_PASSWORD" \
            DEFAULT_REPO_PATTERN="$DEFAULT_REPO_PATTERN" \
            DEFAULT_REPO_PATTERN_ODOO="$DEFAULT_REPO_PATTERN_ODOO" \
            UNACCENT="$UNACCENT" \
            PGUSER="$PGUSER" \
            PGPASSWORD="$PGPASSWORD" \
            PGHOST="$PGHOST" \
            PGPORT=$PGPORT \
            PGDATABASE="$PGDATABASE" \
            PROXY_MODE="$PROXY_MODE" \
            SMTP_SERVER="$SMTP_SERVER" \
            SMTP_PORT=$SMTP_PORT \
            SMTP_USER="$SMTP_USER" \
            SMTP_PASSWORD="$SMTP_PASSWORD" \
            SMTP_SSL="$SMTP_SSL" \
            EMAIL_FROM="$EMAIL_FROM" \
            WITHOUT_DEMO="$WITHOUT_DEMO"
ONBUILD ARG LOCAL_CUSTOM_DIR=./custom
ONBUILD COPY --chown=odoo:odoo $LOCAL_CUSTOM_DIR /opt/odoo/custom
ONBUILD RUN fix_permissions

# https://docs.python.org/3/library/logging.html#levels
ONBUILD ARG LOG_LEVEL=INFO
ONBUILD RUN mkdir -p /opt/odoo/custom/ssh \
            && ln -s /opt/odoo/custom/ssh ~root/.ssh \
            && chmod -R u=rwX,go= /opt/odoo/custom/ssh \
            && sync
ONBUILD ARG DB_VERSION=latest
ONBUILD RUN /opt/odoo/common/build && sync
ONBUILD VOLUME ["/var/lib/odoo"]
ONBUILD USER odoo
