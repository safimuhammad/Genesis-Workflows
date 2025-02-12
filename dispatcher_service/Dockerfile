FROM python:3.9-slim

WORKDIR /app

# Copy the entire dispatcher_service directory
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables if needed
ENV PYTHONPATH=/app

# Command to run the service
CMD ["python", "-m", "app.main"]
