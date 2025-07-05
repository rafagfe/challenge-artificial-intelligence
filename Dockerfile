FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
    --disable-pip-version-check \
    -r /tmp/requirements.txt \
    && find /opt/venv -type d -name "__pycache__" -exec rm -rf {} + \
    && find /opt/venv -type f -name "*.pyc" -delete \
    && find /opt/venv -type f -name "*.pyo" -delete \
    && find /opt/venv -type d -name "tests" -exec rm -rf {} + \
    && find /opt/venv -type d -name "test" -exec rm -rf {} + \
    && rm -rf /opt/venv/lib/python3.11/site-packages/pip \
    && rm -rf /opt/venv/lib/python3.11/site-packages/setuptools

# Final production image
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libgl1-mesa-glx \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    STREAMLIT_HOME=/app/.streamlit \
    STREAMLIT_CONFIG_DIR=/app/.streamlit \
    HOME=/root

# Create app directory and required folders
WORKDIR /app
RUN mkdir -p files_chat/audios files_chat/videos files_chat/states_audio_video .streamlit

# Copy application code 
COPY src/ ./src/
COPY resources/ ./resources/

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "src/main.py", "--server.headless", "true", "--server.address=0.0.0.0", "--server.port=8501"] 