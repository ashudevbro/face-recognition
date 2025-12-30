FROM python:3.11-slim

# Install system dependencies including CMake for dlib
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv and set PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt .

# Install dependencies using uv
RUN /root/.local/bin/uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Create database directory
RUN mkdir -p database

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

