FROM python:3.12-slim

WORKDIR /app

COPY ./bot/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "./app/main.py"]
