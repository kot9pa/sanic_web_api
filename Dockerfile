# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the application files
COPY requirements.txt alembic.ini .env /app/
COPY /src /app/src
COPY /sanic_session /app/sanic_session
COPY /migration /app/migration

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Command to run your application
#CMD ["python", "src/server.py"]
ENTRYPOINT [ "" ]