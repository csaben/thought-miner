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
    python3-dev \
    espeak \
    libespeak-dev \
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

# TODO: should not be needed after we make data-access a pypi thing
# local package dependency injection (literally a hard copy for a bit, sucks)
# wait this can actually work with the compose using context to set to above
# and adjusting the source=tht-miner-transcribe
COPY thought-miner-data-access /opt/thought-miner-data-access

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=thought-miner-alignment/uv.lock,target=uv.lock \
    --mount=type=bind,source=thought-miner-alignment/pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
# Add project files individually for better layer caching
COPY thought-miner-alignment/LICENSE.txt ./LICENSE.txt
COPY thought-miner-alignment/MANIFEST.in ./MANIFEST.in
COPY thought-miner-alignment/README.md ./README.md
COPY thought-miner-alignment/pyproject.toml ./pyproject.toml
COPY thought-miner-alignment/src/ ./src/

# Install project in editable mode with support for private pip configs
# RUN --mount=type=secret,id=pip,target=/etc/pip.conf \
#     uv pip install -e .

RUN uv pip install numpy
# how to hack around the aeneas prebuild with numpy issue
# https://docs.astral.sh/uv/pip/compatibility/#pep-517-build-isolation:~:text=a%20specific%20index.-,PEP%20517%20build%20isolation,-uv%20uses%20PEP
RUN uv pip install setuptools
RUN uv pip install aeneas --no-build-isolation
RUN uv pip install  .
RUN uv pip install -e ../thought-miner-data-access

# Place executables in the environment at the front of the path
ENV PATH="/opt/app/.venv/bin:$PATH"


# TODO: update to be used alongside docker-compose.yml
EXPOSE 8000

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []
# Set the info to be default for now 
CMD ["uv", "run", "thought-miner-alignment", "start-server"]