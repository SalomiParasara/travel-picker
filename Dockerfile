# Python base (small)
FROM python:3.11-slim

# Keep Python fast & logs unbuffered; smaller layers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Workdir
WORKDIR /app

# Install deps first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# (Optional but recommended) run as non-root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# App listens on 8000
EXPOSE 8000

# Start the app (dev-friendly). For prod, see the Gunicorn option below.
CMD ["python", "app.py"]
