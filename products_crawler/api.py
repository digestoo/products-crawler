# #!/usr/bin/python3

from klein import run, route, Klein
app = Klein()
import os

import json
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from spiders.products_crawler import ProductsCrawler


class MyCrawlerRunner(CrawlerRunner):
    """
    Crawler object that collects items and returns output after finishing crawl.
    """
    def crawl(self, crawler_or_spidercls, *args, **kwargs):
        self.items = []
        crawler = self.create_crawler(crawler_or_spidercls)

        crawler.signals.connect(self.item_scraped, signals.item_scraped)

        dfd = self._crawl(crawler, *args, **kwargs)

        dfd.addCallback(self.return_items)
        return dfd

    def item_scraped(self, item, response, spider):
        self.items.append(item)

    def return_items(self, result):
        return self.items


def return_spider_output(output):
    return json.dumps(output)


@app.route("/ecommerce/<domain>")
def getdata(request,domain):
    min_item_count = int(request.args.get(b'itemcount',[10000])[0])
    timeout = int(request.args.get(b'timeout',[10])[0])

    runner = MyCrawlerRunner({'CLOSESPIDER_ITEMCOUNT':min_item_count,
        'CLOSESPIDER_TIMEOUT':timeout})
    spider = ProductsCrawler()
    deferred = runner.crawl(spider,start_urls=['http://%s'%domain])
    deferred.addCallback(return_spider_output)
    
    return deferred




# @app.route('/product-url', methods=['POST'])
# def endpoint_check_if_product_url(request):
#     content = json.loads(request.content.read())
#     url = content['url']
#     features = features_extract(url)
#     product_score = predict_probability(product_url_clf,features)
#     response = json.dumps({'score':product_score})
#     return response



resource = app.resource

app.run("0.0.0.0", 5006)
