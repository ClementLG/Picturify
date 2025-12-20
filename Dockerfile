FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENV FLASK_APP=run.py

ENTRYPOINT ["./entrypoint.sh"]
