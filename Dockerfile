FROM python:3.12-slim

# System dependencies
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    apt-utils \
    libmediainfo0v5 \
    sqlite3 \
    libgl1 \
    libglib2.0-0 \
    libxml2-dev \
    libxslt-dev \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app


# Install python dependencies
COPY package.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r package.txt


# Copy source
COPY . .


# Permission startup script
RUN chmod +x start.sh


# Python runtime settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1


# Railway port
EXPOSE 7860-8000


# Start bot
ENTRYPOINT ["./start.sh"]