# Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./market_analysis_app /app/market_analysis_app

CMD ["python", "market_analysis_app/main.py"]
