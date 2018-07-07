# ProductsCrawler

Simple scraper to get products from eshop site.

## Requirement

Python3 or docker machine

## Run API

### Manual 

```bash
git clone git@github.com:digestoo/products-crawler.git
cd products-crawler
pip install -r requirements.txt
cd products_crawler
python api.py
```

### Docker

```bash
docker pull mdruzkowski/products-crawler
docker run -it -p 5006:5006 mdruzkowski/products-crawler
```

## Making requests

```bash
curl -XGET -H "Content-Type: application/json" http://localhost:5006/ecommerce/<domain>
```

GET params:

- `domain`

Additional params:
- `itemcount` - info for crawler to stop after `itemcount` items
- `timeout` - info for crawler to stop after `timeout` seconds

Example:
```bash
curl -XGET -H "Content-Type: application/json" http://localhost:5006/ecommerce/eobuwie.com.pl?itemcount=1&timeout=5
```
