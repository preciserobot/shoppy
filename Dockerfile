# Base image for Python
## based on debian/bookworm (12) ~= ubuntu/22.04 LTS
FROM python:3.10 as basebuild

# Install Redis and libs
RUN apt-get update && apt-get install -y \
    inetutils-ping \
    less \
    vim \
    redis-server

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip

# Set working directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 8000
EXPOSE 6379

######################
## Production image ##
######################

FROM basebuild as production

# Copy project
COPY . /code/

# Command to run Redis and FastAPI server simultaneously
SHELL ["/bin/bash", "-c"]
CMD ["./start.sh"]
