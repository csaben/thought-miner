# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Configure environment variables
# ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install system dependencies in a single layer + ffmpeg
RUN apt-get update --fix-missing --no-install-recommends && \
    apt-get install -y \
    curl \
    git \
    ffmpeg \ 
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Set working directory
WORKDIR /opt/app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# NOTE: this didnt change anything, autosync for python still doesnwork
COPY thought-miner-data-access /opt/thought-miner-data-access

# Install dependencies first
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=thought-miner-embeddings/uv.lock,target=uv.lock \
    --mount=type=bind,source=thought-miner-embeddings/pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy project metadata files
COPY thought-miner-embeddings/LICENSE.txt \
     thought-miner-embeddings/MANIFEST.in \
     thought-miner-embeddings/README.md \
     thought-miner-embeddings/pyproject.toml \
     thought-miner-embeddings/uv.lock \
     ./

# Create src directory explicitly
RUN mkdir -p /opt/app/src

# Copy initial source code (will be overridden by volume mount)
COPY thought-miner-embeddings/src/ ./src/

# Install in development mode
RUN uv pip install .
RUN uv pip install -e ../thought-miner-data-access
# bruh

ENV PATH="/opt/app/.venv/bin:$PATH"

EXPOSE 8001

ENTRYPOINT []
CMD ["uv", "run", "thought-miner-embeddings", "start-server"]