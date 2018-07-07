FROM python:3

MAINTAINER mdruzkowski@digestoo.com
WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y python3-numpy python3-scipy

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR  /usr/src/app/products_crawler

CMD PYTHONPATH=${PWD} twistd -n web --class=api.resource

EXPOSE 5006