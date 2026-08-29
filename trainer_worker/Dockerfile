FROM python:3.10-slim

WORKDIR /app

# Install system deps needed for building some python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	wget \
	&& rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

CMD ["python", "worker.py"]
