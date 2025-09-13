# --- Stage 1: Build Environment ---
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .

# 🔹 Added system dependencies for PyTorch & OpenCV
# - gcc: needed to compile some Python packages
# - libgl1 & libglib2.0-0: needed by OpenCV for image/video processing
RUN apt-get update && apt-get install -y \
    gcc \
    libgl1 \
    libglib2.0-0 \
    && pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final Production Image ---
FROM python:3.9-slim

# 🔹 Only keep runtime libraries (lighter than builder stage)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 🔹 Copy already-built Python packages from builder (saves rebuild time)
COPY --from=builder /usr/local /usr/local

# Copy app source code
COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
