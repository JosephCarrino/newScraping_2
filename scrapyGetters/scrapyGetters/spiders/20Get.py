#!/usr/bin/env python

import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
from datetime import datetime, timedelta
import time
from os import path
import json
from scrapy.crawler import CrawlerProcess
# import vcr
from urllib.request import urlopen

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
ARCH_URL = "https://www.tagesschau.de/multimedia/video/videoarchiv2.html"
BASE_URL = "https://www.tagesschau.de"

class A20getSpider(scrapy.Spider):
    name = '20Get'
    allowed_domains = [ARCH_URL]
    start_urls = [ARCH_URL]

    def check20Tagess(self, box) -> bool:
        if box.css(".headline").css("a::text").get().rstrip() == "tagesschau" and box.css(".dachzeile::text").get()[11:16] == "20:00":
            return True
        else:
            return False
    
    def parse(self, response):
        boxes = response.css(".viewB")
        toRet= []
        for box in boxes:
            box= box.css(".teaser")
            if self.check20Tagess(box):
                toRet.append(box)   
                             
        
        for box in toRet:
            findTitle= box.css(".teasertext")
            titles= findTitle.css('a::text').get().split(",")
            contents= ""
            findUrl= box.css(".headline")
            urls= BASE_URL + findUrl.xpath('.//a').css('::attr(href)').get()
            findDate= str(box.css("p::text").get())[0:10]
            dates= datetime.strptime(findDate, "%d.%m.%Y").strftime("%B %d, %Y")
            edition= []
            i= 0
            for title in titles:
                scraped_info = {
                    'title': title,
                    'date_raw': dates,
                    'date': datetime.strptime(dates, "%B %d, %Y").strftime("%Y-%m-%d"),
                    'url': response.request.url,
                    'url_news': urls,
                    'content': contents,
                    'ranked': str(i),
                    'epoch': time.time(),
                    'language': "DE",
                    'source': "Tagesschau"
                }
                i+=1
                edition.append(scraped_info)

            base_name = f"{str(edition[0]['date'])}.json"
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/DE/Tagesschau"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(edition, f, indent=4, ensure_ascii=False)
                f.write("\n")
            
            global testdir
            testdir = f"{scraped_data_filepath}"


         
if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)', 
    })

    process.crawl(A20getSpider)
    process.start() 
    f = open(testdir)
    response = json.load(f)
    f.close()
    with vcr.use_cassette('fixtures/vcr_cassettes/Tagesschau.yaml'):
        myres = urlopen(ARCH_URL).read()
        if len(myres) > 0:
            assert 0 < len(response)  
            assert response[0]['title'] is not None 
            for thisresp in response:  
                assert str.encode(thisresp['title']) in myres  
                assert thisresp['url_news'] is not None
            