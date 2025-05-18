# Use an official Python runtime
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Java
RUN apt-get update && apt-get install -y openjdk-17-jdk && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Create a working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the Django project
COPY . .

# Run migrations and start the server
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "parking.wsgi"]
