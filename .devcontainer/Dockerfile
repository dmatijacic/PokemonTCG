# Use Python 3.11 to ensure pygbag compatibility
FROM python:3.12

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get -y update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# upgrade pip
RUN pip install --upgrade pip

# Install Python packages
RUN pip install --no-cache-dir pygame pygbag requests pydantic==2.11.7 pydantic-core==2.33.2

# Set working directory
WORKDIR /workspace

CMD [ "bash" ]
