FROM ubuntu:18.04

RUN apt-get update -y && apt upgrade -y && apt-get install -y python3 && apt-get install python3-pip -y

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]