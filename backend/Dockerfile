FROM python:3.11-slim as builder

# Cài tool để build llama-cpp-python
RUN apt-get update --allow-releaseinfo-change --fix-missing && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libopenblas-dev \
        git \
        curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt

# Nâng cấp pip
RUN python -m pip install --upgrade pip setuptools wheel

# Cài dependencies
RUN pip install --no-cache-dir -r requirements.txt


# ------------------------
# Final runtime image
# ------------------------
FROM python:3.11-slim

RUN apt-get update --allow-releaseinfo-change --fix-missing && \
    apt-get install -y --no-install-recommends \
        libopenblas-dev \
        libgomp1 \
        ffmpeg \
        curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy from builder
COPY --from=builder /usr/local /usr/local

COPY . .

# Env tối ưu cho CPU
ENV OMP_NUM_THREADS=4
ENV MKL_NUM_THREADS=4
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
