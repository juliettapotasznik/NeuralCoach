FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY generator.py .
COPY exercises_dataset.csv .

EXPOSE 8000

CMD ["uvicorn", "generator:app", "--host", "0.0.0.0", "--port", "8000"]

