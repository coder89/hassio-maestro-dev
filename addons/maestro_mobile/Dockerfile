ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.23
# hadolint ignore=DL3006: We keep BUILD_FROM as a build-arg so CI can override it when needed.
FROM ${BUILD_FROM}

# Install necessary packages
# hadolint ignore=DL3018: pinning apk packages in this image is brittle; keep as-is or add pins later.
RUN apk add --no-cache \
  curl \
  unzip \
  bash \
  build-base \
  cmake \
  git \
  json-c-dev \
  libwebsockets-dev \
  android-tools \
  openjdk17-jre-headless \
  dos2unix \
  zlib-dev \
  libuv-dev \
  openssl-dev \
  mosquitto-clients \
  tini

# Build ttyd from source (cleaned up after install)
RUN git clone https://github.com/tsl0922/ttyd.git /tmp/ttyd \
  && cd /tmp/ttyd \
  && mkdir build \
  && cd build \
  && cmake .. \
  && make -j$(nproc) \
  && make install \
  && cd / \
  && rm -rf /tmp/ttyd

# Install Maestro CLI
ENV MAESTRO_VERSION=1.39.2
RUN curl -L "https://github.com/mobile-dev-inc/maestro/releases/download/cli-${MAESTRO_VERSION}/maestro.zip" -o maestro.zip \
  && unzip maestro.zip -d /opt/maestro \
  && rm maestro.zip \
  && ln -s /opt/maestro/maestro/bin/maestro /usr/local/bin/maestro \
  && chmod +x /usr/local/bin/maestro

# Copy root filesystem
COPY rootfs /

# Convert scripts to Unix format and set executable permissions
RUN dos2unix /run.sh /usr/local/bin/restricted-shell.sh /usr/local/bin/adb_connect.sh /usr/local/bin/maestro_service.sh
RUN chmod +x /run.sh /usr/local/bin/restricted-shell.sh /usr/local/bin/adb_connect.sh /usr/local/bin/maestro_service.sh

# Expose ADB and ttyd ports
EXPOSE 5037 7681

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# Labels
LABEL \
  io.hass.name="${BUILD_NAME}" \
  io.hass.description="${BUILD_DESCRIPTION}" \
  io.hass.arch="${BUILD_ARCH}" \
  io.hass.type="addon" \
  io.hass.version="${BUILD_VERSION}" \
  maintainer="coder89 <https://github.com/coder89>" \
  org.opencontainers.image.title="${BUILD_NAME}" \
  org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
  org.opencontainers.image.vendor="coder89 <https://github.com/coder89>" \
  org.opencontainers.image.authors="coder89 <https://github.com/coder89>" \
  org.opencontainers.image.licenses="MIT" \
  org.opencontainers.image.url="https://github.com/${BUILD_REPOSITORY}" \
  org.opencontainers.image.source="https://github.com/${BUILD_REPOSITORY}" \
  org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/main/README.md" \
  org.opencontainers.image.created="${BUILD_DATE}" \
  org.opencontainers.image.revision="${BUILD_REF}" \
  org.opencontainers.image.version="${BUILD_VERSION}"

# Use tini as the init system
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/run.sh"]
