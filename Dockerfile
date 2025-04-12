FROM python:3.10-slim-buster

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . /app

EXPOSE 8080

#CMD ["python3", "app.py"]
CMD ["gunicorn", "--workers=4", "--timeout=120", "main:app"]