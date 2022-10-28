FROM continuumio/miniconda3

RUN apt-get update && apt-get install libgl1 -y && conda install -c conda-forge dlib -y

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "app.py"]