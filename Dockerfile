FROM python:3.9.5-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update \
    && apt-get -y install libpq-dev gcc
    
RUN pip3 install -r requirements.txt

RUN mkdir templates
#COPY templates ./templates
COPY gera_mapa.py .
COPY flask_server.py .

RUN python3 gera_mapa.py
RUN mv map.html /app/templates/

ENV FLASK_APP=flask_server.py  
# requerimento para rodar o flask run

CMD ["flask", "run", "--host","0.0.0.0", "--port","5000"]