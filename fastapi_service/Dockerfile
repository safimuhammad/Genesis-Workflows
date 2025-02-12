FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY fastapi_service/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app
RUN pip install -r requirements.txt
WORKDIR /app
# Expose port
EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]