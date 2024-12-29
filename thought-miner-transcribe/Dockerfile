# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Configure environment variables
# ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install system dependencies in a single layer
RUN apt-get update --fix-missing --no-install-recommends && \
    apt-get install -y \
    curl \
    git \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt/app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# TODO: should not be needed after we make data-access a pypi thing
# local package dependency injection (literally a hard copy for a bit, sucks)
# wait this can actually work with the compose using context to set to above
# and adjusting the source=tht-miner-transcribe
COPY thought-miner-data-access /opt/thought-miner-data-access

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=thought-miner-transcribe/uv.lock,target=uv.lock \
    --mount=type=bind,source=thought-miner-transcribe/pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
# Add project files individually for better layer caching
COPY thought-miner-transcribe/LICENSE.txt ./LICENSE.txt
COPY thought-miner-transcribe/MANIFEST.in ./MANIFEST.in
COPY thought-miner-transcribe/README.md ./README.md
COPY thought-miner-transcribe/pyproject.toml ./pyproject.toml
COPY thought-miner-transcribe/src/ ./src/
# specific to uv (docs naively assuem this is in your current dir and add wholesale)
COPY thought-miner-transcribe/uv.lock ./uv.lock

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev 

# Install project in editable mode with support for private pip configs
# RUN --mount=type=secret,id=pip,target=/etc/pip.conf \
#     uv pip install -e .

# Place executables in the environment at the front of the path
ENV PATH="/opt/app/.venv/bin:$PATH"


# TODO: update to be used alongside docker-compose.yml
EXPOSE 8000

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []
# Set the info to be default for now 
CMD ["thought-miner-transcribe", "start-server"]