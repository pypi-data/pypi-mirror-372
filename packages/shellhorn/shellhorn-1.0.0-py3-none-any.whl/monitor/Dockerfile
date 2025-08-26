FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user for security
RUN groupadd --gid 1001 shellhorn && \
    useradd --uid 1001 --gid shellhorn --shell /bin/bash --create-home shellhorn

# Install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Create directories
RUN mkdir -p /config /app && \
    chown -R shellhorn:shellhorn /config /app

# Copy application
COPY shellhorn_monitor.py /app/
RUN chown shellhorn:shellhorn /app/shellhorn_monitor.py

# Switch to non-root user
USER shellhorn
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s = socket.socket(); s.settimeout(5); result = s.connect_ex(('${MQTT_BROKER:-localhost}', int('${MQTT_PORT:-1883}'))); s.close(); exit(result)"

# Default command
CMD ["python", "shellhorn_monitor.py"]

# Labels for best practices
LABEL maintainer="shellhorn-monitor"
LABEL description="Shellhorn MQTT monitor for detecting orphaned commands"
LABEL version="1.0.0"