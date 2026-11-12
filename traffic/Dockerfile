# Traffic generator image (runs as the `loadgen` EKS deployment, or locally via compose --profile load).
FROM public.ecr.aws/docker/library/python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --require-hashes --no-deps -r requirements.txt  # hash-pinned lock (deploy/scripts/lock.sh)
COPY loadgen.py .
RUN useradd -m -u 1000 loadgen
USER loadgen
ENV PYTHONUNBUFFERED=1 HEARTBEAT_FILE=/tmp/loadgen.heartbeat
# No HTTP server here: healthy while the generator keeps refreshing its heartbeat file.
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD ["python", "-c", "import os, sys, time; p = os.environ['HEARTBEAT_FILE']; sys.exit(0 if os.path.exists(p) and time.time() - os.path.getmtime(p) < 90 else 1)"]
CMD ["python", "loadgen.py"]
