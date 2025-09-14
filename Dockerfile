# =========================
# Stage 1: Build Stage
# =========================
FROM python:3.9-slim as builder

WORKDIR /app

# Copy only requirements first (better caching)
COPY requirements.txt .

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (CPU-only PyTorch for smaller size)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt \
    && pip check

# =========================
# Stage 2: Final Stage (Distroless)
# =========================
FROM gcr.io/distroless/python3

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY run.py .
COPY app/ ./app

# Expose the port
EXPOSE 5000

# Start the app (distroless requires exec form)
CMD ["python", "run.py"]

