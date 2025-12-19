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
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm && \
    python -m nltk.downloader punkt && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy project
COPY . .

# Collect static files (if using whitenoise)
RUN python manage.py collectstatic --noinput

# Create a writable directory for standard non-root user (good practice, optional for Spaces but safe)
RUN mkdir -p /app/static root && chmod 777 /app/static root

# Expose port (Hugging Face Spaces uses 7860)
# Expose port (Standard is 8000)
EXPOSE 8000

# Run Migrations and Gunicorn
# Run Migrations and Gunicorn in a shell
# Create empty DB file to avoid permission issues
RUN touch db.sqlite3 && chmod 777 db.sqlite3

# Run Migrations and Gunicorn
# Using --timeout 400 to allow heavy models to download/load if needed
CMD ["sh", "-c", "python manage.py migrate && gunicorn news_guardian.wsgi:application --bind 0.0.0.0:8000 --workers 1 --timeout 400"]
