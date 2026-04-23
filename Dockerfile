FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

# Initialize database and run app
CMD ["sh", "-c", "python -c \"from app import create_app; app = create_app(); app.app_context().push()\" && python run.py"]
