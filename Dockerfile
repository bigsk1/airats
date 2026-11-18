FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==27.0.1

COPY app.py Main.py ./
COPY templates/ templates/
COPY static/ static/
COPY images/fish.jpg images/fish.jpg

ENV PYTHONUNBUFFERED=1
USER 10001:10001
EXPOSE 5000

CMD ["gunicorn", "--workers", "2", "--no-control-socket", "--bind", "0.0.0.0:5000", "app:app"]
