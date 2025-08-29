# Multi-stage Dockerfile for MicroRapids API Runtime

# Stage 1: Build environment
FROM rust:alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    musl-dev \
    openssl-dev \
    openssl-libs-static \
    pkgconfig \
    git

# Create app directory
WORKDIR /app

# Copy manifests
COPY Cargo.toml Cargo.lock ./

# Copy source code
COPY src ./src
COPY examples ./examples

# Build arguments
ARG VERSION=dev
ARG COMMIT=unknown

# Build the application
RUN --mount=type=cache,target=/app/target \
    --mount=type=cache,target=/usr/local/cargo/registry \
    cargo build --release --all-features && \
    cargo build --release -p mrapids-agent && \
    cp target/release/mrapids /app/mrapids && \
    cp target/release/mrapids-agent /app/mrapids-agent

# Stage 2: Runtime environment
FROM alpine:3.19

# Install runtime dependencies
RUN apk add --no-cache \
    ca-certificates \
    libgcc \
    openssl \
    curl \
    jq

# Create non-root user
RUN addgroup -g 1000 mrapids && \
    adduser -D -u 1000 -G mrapids mrapids

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/config && \
    chown -R mrapids:mrapids /app

WORKDIR /app

# Copy binaries from builder
COPY --from=builder --chown=mrapids:mrapids /app/mrapids /app/mrapids
COPY --from=builder --chown=mrapids:mrapids /app/mrapids-agent /app/mrapids-agent

# Copy configuration and docs (if they exist)
# Using shell trick to handle missing files gracefully
COPY --chown=mrapids:mrapids SECURITY.md ./ 
COPY --chown=mrapids:mrapids examples ./examples

# Build metadata
ARG VERSION=dev
ARG COMMIT=unknown
ARG BUILD_DATE

# Labels
LABEL org.opencontainers.image.title="MicroRapids API Runtime" \
      org.opencontainers.image.description="High-performance API runtime for microservices" \
      org.opencontainers.image.vendor="MicroRapids" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${COMMIT}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.source="https://github.com/microrapids/api-runtime" \
      org.opencontainers.image.licenses="MIT"

# Environment variables
ENV MRAPIDS_VERSION=${VERSION} \
    MRAPIDS_COMMIT=${COMMIT} \
    MRAPIDS_DATA_DIR=/app/data \
    MRAPIDS_LOG_DIR=/app/logs \
    MRAPIDS_CONFIG_DIR=/app/config \
    RUST_LOG=info \
    RUST_BACKTRACE=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/app/mrapids", "health"] || exit 1

# Switch to non-root user
USER mrapids

# Expose default port
EXPOSE 8080

# Volume mounts
VOLUME ["/app/data", "/app/logs", "/app/config"]

# Default command
ENTRYPOINT ["/app/mrapids"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8080"]