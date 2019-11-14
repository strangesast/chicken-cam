FROM python:3.8

WORKDIR /app

COPY server/requirements.txt .

RUN pip install -r requirements.txt

COPY ./server/. /app/

CMD ["python3.8", "main.py"]
