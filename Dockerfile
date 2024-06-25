FROM python:3.10.6-slim-bullseye

WORKDIR /app

ARG GEMFURY_URL

ENV GEMFURY_URL=$GEMFURY_URL

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

ENV PYTHONPATH = $PYTHONPATH:/app/

CMD ["gunicorn", "main:server", "--timeout", "300"]
