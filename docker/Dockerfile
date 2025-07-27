# AI Agent Seller Backend - Optimized Multi-stage Dockerfile with Conda
# Stage 1: Base image with conda
FROM continuumio/miniconda3:latest as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    CONDA_AUTO_UPDATE_CONDA=false \
    PATH=/opt/conda/bin:$PATH

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    curl \
    netcat-openbsd \
    libpq-dev \
    postgresql-client \
    ffmpeg \
    libsndfile1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    libstdc++6 \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Stage 2: Dependencies installation
FROM base as dependencies

# Set working directory
WORKDIR /app

# Copy conda environment file
COPY conda-environment-docker.yml /tmp/conda-environment-docker.yml

# Create conda environment and install dependencies
RUN conda env create -f /tmp/conda-environment-docker.yml && \
    conda clean -afy && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.pyc' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

# Activate environment and install TTS separately
ENV CONDA_DEFAULT_ENV=ai_seller
ENV PATH=/opt/conda/envs/ai_seller/bin:$PATH

# Install TTS separately to avoid dependency conflicts
RUN /opt/conda/envs/ai_seller/bin/pip install tts==0.22.0 --no-deps && \
    /opt/conda/envs/ai_seller/bin/pip install coqpit==0.0.17 && \
    /opt/conda/envs/ai_seller/bin/pip install librosa==0.10.0 && \
    /opt/conda/envs/ai_seller/bin/pip install soundfile==0.12.1 && \
    /opt/conda/envs/ai_seller/bin/pip install "numpy>=2.0.0,<2.3.0" && \
    /opt/conda/envs/ai_seller/bin/pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu

# Stage 3: Final production image
FROM base as production

# Copy conda environment from dependencies stage
COPY --from=dependencies /opt/conda /opt/conda

# Set environment
ENV CONDA_DEFAULT_ENV=ai_seller
ENV PATH=/opt/conda/envs/ai_seller/bin:$PATH

# Create app user for security
RUN adduser --disabled-password --gecos '' --uid 1000 appuser

# Set working directory and ownership
WORKDIR /app
RUN chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Create necessary directories
RUN mkdir -p /app/models /app/uploads /app/cache /app/logs /app/temp /app/assets

# Copy application code
COPY --chown=appuser:appuser app/ /app/app/
COPY --chown=appuser:appuser run.py /app/
COPY --chown=appuser:appuser requirements/ /app/requirements/

# Copy assets directory structure (but not the large model files - they'll be mounted)
COPY --chown=appuser:appuser assets/ /app/assets/

# Copy and set up entrypoint script
USER root
COPY docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh && chown appuser:appuser /docker-entrypoint.sh
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/status/health || exit 1

# Set entrypoint and default command
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]