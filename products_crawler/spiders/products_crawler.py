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
from bs4 import BeautifulSoup

import extruct

import tldextract
import lxml.html

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
print('syspath',sys.path)

from producturl import check_if_product_url

def url_to_domain(url):
    p = tldextract.extract(url)
    if p.subdomain:
        return '.'.join(p)
    else:
        return '%s.%s'%(p.domain,p.suffix)


tld = tldextract.TLDExtract(extra_suffixes=['com.ru'])

from scrapy.linkextractors import LinkExtractor
 
class ProductsCrawler(scrapy.Spider):
    name = "products_crawler"
    custom_settings = {
        'DEPTH_LIMIT':3,
        'DNS_TIMEOUT':5,
        # 'CLOSESPIDER_TIMEOUT':15,
        'LOG_ENABLED':True,
        # 'CLOSESPIDER_ITEMCOUNT': 1000,
        'CONCURRENT_REQUEST':2,
        'DOWNLOAD_TIMEOUT':3,
        'RETRY_TIMES':1,
        'FEED_FORMAT':'json',
        'USER_AGENT':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.102 Safari/537.36",
        
        'DEFAULT_REQUEST_HEADERS': {
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },

        'LOG_LEVEL':'DEBUG'
    }


    def parse(self, response):
        bad_keywords = ['koszyk','basket','cart','faq','blog','login','news','aktualnosc','zakup','help','pomoc','regulamin']
        links = LinkExtractor().extract_links(response) 
        idx = 0        
        for link in links:
            ok = True
            for keyword in bad_keywords:
                if keyword  in link.url.lower():
                    ok = False
            if ok == False:
                continue

            if tldextract.extract(link.url)[1] == tldextract.extract(response.url)[1]:
                idx+=1
                product_score = check_if_product_url(link.url)

                if product_score > 80:
                    yield {'url':link.url, 'score': product_score}
                else:
                    if idx>10 and idx<20:
                        yield Request(url=link.url)