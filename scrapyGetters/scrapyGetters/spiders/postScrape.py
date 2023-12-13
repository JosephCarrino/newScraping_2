#!/usr/bin/env python

import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
from datetime import datetime, timedelta
import time
from os import path
import json

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"www.ilpost.it"
ARCH_URLS = [f"https://{BASE_URL}/mondo/"]

place_dict= {'https://www.ilpost.it/': "First_Page",
            'https://www.ilpost.it/mondo/': "Abroad",
            'https://www.ilpost.it/politica/': "Politics",
            'https://www.ilpost.it/economia/': "Economics"}


class PostscrapeSpider(scrapy.Spider):
    name = 'postScrape'
    allowed_domains = [BASE_URL]
    start_urls = ARCH_URLS

    def parse(self, response):
        articles= response.css("#content").css("article")
        titles= []
        dates_raw= []
        dates= []
        urls= []
        contents= []
        placeds=[]
        rankeds= []
        

        i= 0
        for article in articles:
            tourl= article.css("header").css("figure").css("a::attr(href)").get()
            urls.append(tourl)
            try:
                todate=datetime.strptime(tourl[22:32], "%Y/%m/%d")
            except:
                todate= datetime.now()
            dates.append(todate.strftime("%Y-%m-%d"))
            dates_raw.append(todate.strftime("%B %d, %Y"))
            info= article.css(".entry-content")
            titles.append(info.css("h2").css("a::text").get())
            contents.append(info.css("p").css("a::text").get())
            placeds.append(place_dict[response.url])
            rankeds.append(i)
            i+=1
         
        edition= []
        i= 0
        for item in zip(titles, dates_raw, dates, urls, contents, rankeds, placeds):
            i+=1
            yield scrapy.Request(item[3], callback= self.getFullContent, meta= {'data': item, 'currelem': i, 'edition': edition, 'oldurl': response.request.url})
            
        

    def getFullContent(self, response):
        fullcont = response.css("#singleBody").css("p::text").getall()
        content= ''.join(fullcont)
        
        item = response.meta.get('data')
        scraped_info= {
                'title': item[0],
                'date_raw': item[1],
                'date': item[2],
                'url': response.meta.get('oldurl'),
                'news_url': item[3],
                'subtitle': item[4],
                'content': content,
                'ranked': item[5],
                'placed': item[6],
                'epoch': time.time(),
                'language': 'IT',
                'source': "ilPost"
            }
        
        response.meta.get('edition').append(scraped_info)

        if response.meta.get('currelem') == len(item):
            now = datetime.now()
            now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
            now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)

            base_name = f"{now_s}E{now_epoch}.json"
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/IT/ilPost"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(response.meta.get('edition'), f, indent= 4, ensure_ascii=False)
                f.write("\n")