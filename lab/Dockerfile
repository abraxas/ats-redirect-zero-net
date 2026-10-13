# Shared Apache Traffic Server 10.2.0 lab image (ats-10.2.0-lab:local).
# Build context is the pinned trafficserver source tree. Runtime extras
# (python3, iproute2) are for in-netns oracles used by sibling labs.
FROM ubuntu:24.04 AS build

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        brotli \
        ca-certificates \
        cmake \
        g++ \
        libbrotli-dev \
        libcap-dev \
        libfmt-dev \
        libhwloc-dev \
        libjemalloc-dev \
        libluajit-5.1-dev \
        libmagick++-dev \
        libpcre2-dev \
        libpcre3-dev \
        libssl-dev \
        libxml2-dev \
        ninja-build \
        pkg-config \
        python3 \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /src
WORKDIR /src

RUN cmake -S /src -B /build -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local/trafficserver \
        -DBUILD_TESTING=OFF \
        -DBUILD_REGRESSION_TESTING=OFF \
        -DENABLE_AUTEST=OFF \
        -DENABLE_VERIFY_PLUGINS=OFF \
        -DENABLE_DOCS=OFF \
        -DENABLE_EXAMPLE=OFF \
        -DENABLE_QUICHE=OFF \
        -DENABLE_BENCHMARKS=OFF \
        -DBUILD_EXPERIMENTAL_PLUGINS=ON \
        -DLUAJIT=ON \
        -DENABLE_CRIPTS=ON \
        -DJEMALLOC=ON \
    && cmake --build /build --parallel 3 \
    && cmake --install /build

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/usr/local/trafficserver/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        iproute2 \
        libbrotli1 \
        libcap2 \
        libfmt9 \
        libhwloc15 \
        libjemalloc2 \
        libluajit-5.1-2 \
        libmagick++-6.q16-9t64 \
        libpcre2-8-0 \
        libpcre3 \
        libssl3t64 \
        libxml2 \
        python3 \
        zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/trafficserver /usr/local/trafficserver

RUN mkdir -p \
        /usr/local/trafficserver/var/trafficserver \
        /usr/local/trafficserver/var/log/trafficserver \
    && chown -R nobody:nogroup \
        /usr/local/trafficserver/var/trafficserver \
        /usr/local/trafficserver/var/log/trafficserver

EXPOSE 8080
CMD ["traffic_server"]
