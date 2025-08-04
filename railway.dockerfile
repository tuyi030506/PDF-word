# Railway.app 专用 Dockerfile
# Railway对依赖安装更宽松，可能成功安装Pillow

FROM python:3.11-bullseye

# 安装完整的系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先安装Pillow
RUN pip install --upgrade pip
RUN pip install Pillow==10.0.1

# 然后安装其他依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "server.py"] 