# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install setuptools version 66.1
RUN pip install 'setuptools==66.1.1'

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn

# Make sure that the app is listening on all interfaces
ENV FLASK_RUN_HOST=0.0.0.0

# Set up logging
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
ENV LOG_FILE=/var/log/app.log

# Create log directory
RUN mkdir /var/log/flask

# Expose the port that the app is running on
EXPOSE 5000

# Run app.py when the container launches
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

