FROM ubuntu:latest
FROM python:3.7
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY app /api
WORKDIR /api
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]