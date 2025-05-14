# Dockerfile
FROM python:3.10-slim-bookworm

# Install required system packages
RUN apt-get update && apt-get install -y ffmpeg && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Collect static files
ENV SECRET_KEY=dummy_during_build
RUN python manage.py collectstatic --noinput

# Environment variables for Django
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=yttranscriber.settings

# Migrations and server
CMD ["sh", "-c", "python manage.py migrate && gunicorn yttranscriber.wsgi:application --bind 0.0.0.0:8000"]

