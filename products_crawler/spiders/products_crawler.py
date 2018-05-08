#!/usr/bin/python3
# -*- coding: utf-8 -*-
import scrapy
import os
from scrapy.spiders import CrawlSpider, Rule, SitemapSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, XmlResponse
from scrapy.selector import Selector

import re
import sys, traceback
import slugify
from bs4 import BeautifulSoup

import extruct

import tldextract
import lxml.html

def url_to_domain(url):
    p = tldextract.extract(url)
    if p.subdomain:
        return '.'.join(p)
    else:
        return '%s.%s'%(p.domain,p.suffix)



tld = tldextract.TLDExtract(extra_suffixes=['com.ru'])


from scrapy.linkextractors import LinkExtractor


def parse_product_schema(product_details):
    product = {}
    product['name'] = product_details.get('name',None)
    product['image'] = product_details.get('image',None)
    if product['image'] is not None and isinstance(product['image'],str):
        product['image'] = [product['image']]
    product['brand'] = product_details.get('brand',None)
    product['description'] = product_details.get('description',None)
    product['itemCondition'] = product_details.get('itemCondition',None)
    product['manufacturer'] = product_details.get('manufacturer',None)
    product['color'] = product_details.get('color',None)
    return product

def parse_offers_schema(offers):
    product = {}
    product['price'] = offers.get('price',None)
    product['availability'] = offers.get('availability',None)
    if product['availability'] is not None and 'schema.org' in product['availability']:
        product['availability'] = product['availability'].split('/')[3]
    product['priceCurrency'] = offers.get('priceCurrency',None)
    return product


def get_products_details(text,url):
    all_meta = extruct.extract(text,url)
    product = {}
    microdata = all_meta['microdata']
    product_details = [x for x in microdata if x.get('type','').endswith('Product')]
    if len(product_details) == 1:
        product_details = product_details[0]['properties']
        product.update(parse_product_schema(product_details))
        
        if 'offers' in  product_details:
            offers = product_details['offers']
            product['offers'] = []
            if isinstance(offers,list):
                for x in offers:
                    product['offers'].append(parse_offers_schema(x['properties']))
            else:
                product['offers'].append(parse_offers_schema(offers['properties']))
    
    jsonld = all_meta['json-ld']
    graphdetails = [x for x in jsonld if '@graph' in x]
    if len(graphdetails)>0:
        jsonld = graphdetails[0]['@graph']
    product_details = [x for x in jsonld if x.get('@type','').endswith('Product')]
    if len(product_details) == 1:
        product_details = product_details[0]
        product.update(parse_product_schema(product_details))
        
        if 'offers' in  product_details:
            offers = product_details['offers']
            product['offers'] = []
            if isinstance(offers,list):
                for x in offers:
                    product['offers'].append(parse_offers_schema(x))
            else:
                product['offers'].append(parse_offers_schema(offers))
        
    if len(product) > 0:
        breadcrumb_details = [x for x in microdata if x.get('type','').endswith('BreadcrumbList')]
        if len(breadcrumb_details)>0:
            breadcrumb_list = breadcrumb_details[0]['properties']['itemListElement']
            product['category'] = ' // '.join([x['properties']['name'] for x in breadcrumb_list])
        
        breadcrumb_details = [x for x in jsonld if x.get('@type','').endswith('BreadcrumbList')]
        
        if len(breadcrumb_details)>0:
            breadcrumb_list = breadcrumb_details[0]['itemListElement']
            product['category'] = ' // '.join([x['item']['name'] for x in breadcrumb_list])
    
    return product


 
class ProductsCrawler(scrapy.Spider):
    name = "products_crawler"
    custom_settings = {
        'DEPTH_LIMIT':4,
        'DNS_TIMEOUT':5,
        #'CLOSESPIDER_TIMEOUT':1,
        'LOG_ENABLED':True,
        #'CLOSESPIDER_ITEMCOUNT': 1,
        'CONCURRENT_REQUEST':2,
        'DOWNLOAD_TIMEOUT':10,
        'RETRY_TIMES':1,
        'FEED_FORMAT':'json',
        'USER_AGENT':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.102 Safari/537.36",
        
        'DEFAULT_REQUEST_HEADERS': {
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },

        'LOG_LEVEL':'DEBUG'
    }
    #start_urls = ['https://supertipi.pl/']
    

    def parse(self, response):
            try:
                
                product = get_products_details(response.text, response.url)

                if product == {}:
                    links = LinkExtractor().extract_links(response)         
                    for link in links:
                        #link_slug = slugify.slugify(link.text)
                        if tldextract.extract(link.url)[1] == tldextract.extract(response.url)[1]:
                            yield Request(url=link.url)
                else:
                    product['url'] = response.url
                    yield product

            except Exception as e:
                print(e)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=10, file=sys.stdout)

