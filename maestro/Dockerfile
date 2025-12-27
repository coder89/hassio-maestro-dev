ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-debian:latest
FROM ${BUILD_FROM}

# Install necessary packages and wget for downloading tini
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl wget unzip bash build-essential cmake git libjson-c-dev libwebsockets-dev openjdk-17-jdk-headless android-tools-adb dos2unix && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/tsl0922/ttyd.git

WORKDIR /ttyd
RUN mkdir build
WORKDIR /ttyd/build
RUN cmake .. && \
    make && make install

ARG TARGETARCH

# Install adb / platform-tools in a robust manner:
# - Prefer the Debian package if available for the target architecture
# - For amd64, prefer Google's platform-tools zip (gives latest tools)
# - If packages are not available, try the platform-tools zip as a fallback
RUN case "$TARGETARCH" in \
    "amd64") \
        echo "Fetching latest amd64 platform-tools from Google" && \
        wget -q https://dl.google.com/android/repository/platform-tools-latest-linux.zip -O /tmp/platform-tools.zip && \
        unzip -q /tmp/platform-tools.zip -d /opt && \
        rm /tmp/platform-tools.zip || true ;\
        ;; \
    "arm64" | "arm" | "386") \
        echo "Attempting to install platform-tools from apt for $TARGETARCH" && \
        apt-get update && \
        apt-get install -y --no-install-recommends android-sdk-platform-tools android-tools-adb adb || true && \
        rm -rf /var/lib/apt/lists/* ;\
        ;; \
    *) \
        echo "Unsupported architecture for adb installation: $TARGETARCH - attempting apt install fallback" && \
        apt-get update && \
        apt-get install -y --no-install-recommends android-sdk-platform-tools android-tools-adb adb || true && \
        rm -rf /var/lib/apt/lists/* ;\
        ;; \
    esac && \
    # Verify adb is available; if not present try fetching Google's platform-tools as a fallback
    if ! command -v adb >/dev/null 2>&1 ; then \
        echo "adb not found after package install, attempting platform-tools zip fallback" && \
        wget -q https://dl.google.com/android/repository/platform-tools-latest-linux.zip -O /tmp/platform-tools.zip && \
        unzip -q /tmp/platform-tools.zip -d /opt && \
        rm -f /tmp/platform-tools.zip || true ; \
    fi

ENV PATH="/opt/platform-tools:${PATH}"

# Install Maestro CLI
ENV MAESTRO_VERSION=1.39.2
RUN curl -L "https://github.com/mobile-dev-inc/maestro/releases/download/cli-${MAESTRO_VERSION}/maestro.zip" -o maestro.zip \
  && unzip maestro.zip -d /opt/maestro \
  && rm maestro.zip \
  && ln -s /opt/maestro/maestro/bin/maestro /usr/local/bin/maestro \
  && chmod +x /usr/local/bin/maestro

# Download and install tini based on the target architecture
RUN case "$TARGETARCH" in \
    "amd64") TINI_URL="https://github.com/krallin/tini/releases/download/v0.19.0/tini";; \
    "arm64") TINI_URL="https://github.com/krallin/tini/releases/download/v0.19.0/tini-arm64";; \
    "arm") TINI_URL="https://github.com/krallin/tini/releases/download/v0.19.0/tini-armhf";; \
    "386") TINI_URL="https://github.com/krallin/tini/releases/download/v0.19.0/tini-i386";; \
    *) echo "Unsupported architecture: $TARGETARCH" && exit 1;; \
    esac && \
    wget -q -O /usr/bin/tini $TINI_URL && \
    chmod +x /usr/bin/tini

# Copy root filesystem
COPY rootfs /

# Convert scripts to Unix format and set executable permissions
RUN dos2unix /run.sh /usr/local/bin/restricted-shell.sh /usr/local/bin/adb_connect.sh
RUN chmod +x /run.sh /usr/local/bin/restricted-shell.sh /usr/local/bin/adb_connect.sh

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
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run.sh"]
