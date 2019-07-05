FROM python:3.7

COPY ./app /app
WORKDIR /app
RUN pip install bottle requests aiofiles jinja2 python-multipart itsdangerous pyyaml graphene ujson psycopg2-binary pygresql joblib pymysql sqlalchemy sklearn minio numpy nbconvert nbformat
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install -r requirements.txt
CMD ["python", "main.py"]