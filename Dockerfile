FROM python:3.9-alpine
WORKDIR /app
RUN apk add --no-cache alpine-sdk libffi-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./app.py ./app.py
CMD ["python", "app.py"]