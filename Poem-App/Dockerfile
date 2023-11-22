FROM  --platform=linux/arm/v6 python:latest

## helps avoid apt errors 
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update --allow-unauthenticated && apt install --allow-unauthenticated -y pip && rm -rf /var/lib/apt/lists/*
RUN apt update && apt install -y libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt 
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --upgrade psycopg2

COPY init-postgres-pif.py /app/init-postgres-pif.py
COPY main.py /app/main.py
COPY modules /app/modules
COPY run.sh /app/run.sh
#COPY insert-poem-lyrics.py /app/insert-poem-lyrics.py
#COPY insert-poem-web.py /app/insert-poem-web.py

RUN ["chmod", "+x", "/app/init-postgres-pif.py"]
RUN ["chmod", "+x", "/app/main.py"]
#RUN ["chmod", "+x", "/app/insert-poem-web.py"]
#RUN ["chmod", "+x", " /app/insert-poem-lyrics.py"]

RUN ["chmod", "+x", "/app/run.sh"]
CMD ["/app/run.sh"]
