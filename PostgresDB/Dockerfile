FROM --platform=linux/arm/v6 postgres:latest

## helps avoid apt errors 
ENV DEBIAN_FRONTEND=noninteractive

#install postgresql
RUN apt update && apt install -y python3 && rm -rf /var/lib/apt/lists/*
RUN apt update && apt install -y pip && rm -rf /var/lib/apt/lists/*
RUN apt update && apt install -y net-tools && rm -rf /var/lib/apt/lists/*

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=raspberry

CMD ["postgres"]
