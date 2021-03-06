FROM python:3.6

MAINTAINER mdruzkowski@digestoo.com
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR  /usr/src/app/products_crawler

CMD PYTHONPATH=${PWD} twistd -n web --class=api.resource

EXPOSE 5006