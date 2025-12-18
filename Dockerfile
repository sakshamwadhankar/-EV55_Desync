# Use official Python runtime
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for some ML libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm && \
    python -m nltk.downloader punkt

# Copy project
COPY . .

# Collect static files (if using whitenoise)
RUN python manage.py collectstatic --noinput

# Create a writable directory for standard non-root user (good practice, optional for Spaces but safe)
RUN mkdir -p /app/static root && chmod 777 /app/static root

# Expose port (Hugging Face Spaces uses 7860)
EXPOSE 7860

# Run Gunicorn
CMD ["gunicorn", "news_guardian.wsgi:application", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120"]
