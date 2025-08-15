FROM python:3.11

RUN apt-get update --allow-releaseinfo-change --fix-missing && \
    apt-get install -y \
        build-essential \
        libpango-1.0-0 \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        libffi-dev \
        libglib2.0-0 \
        libxml2 \
        libxslt1.1 \
        shared-mime-info \
        fonts-liberation \
        libjpeg-dev \
        zlib1g-dev \
        libtiff-dev \
        libfreetype6-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*



WORKDIR /app

COPY backend/requirements.txt ./requirements.txt


RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
