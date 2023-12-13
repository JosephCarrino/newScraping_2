#!/usr/bin/env python

import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
from datetime import datetime
import time
from os import path
import json
import dateparser

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"https://www.rts.ch/audio-podcast/2021/audio"

class RtsgetSpider(scrapy.Spider):
    name = 'rtsGet'
    f=open("rtsurls.txt", "r+")
    toGetUrls= f.read()
    toGetUrls = toGetUrls.split("\n")
    toGetUrls = list(dict.fromkeys(toGetUrls))
    allowed_domains = [BASE_URL]
    print(toGetUrls)
    start_urls = toGetUrls

    def parse(self, response):
        chapters= response.css(".audio-chapter-list").css("ul").css("li")
        todate= response.css(".timeframe").css("span")
        todate= dateparser.parse(todate[1].css("::text").get()).date()
        chapters= chapters[1:len(chapters)]
        titles= []
        dates_raw= []
        dates= []
        urls= []
        rankeds= []
        durations= []
        i= 0
        for chapter in chapters:
            urls.append(chapter.css("a::attr(href)").get())
            titles.append(chapter.css(".title::text").get())
            durations.append(chapter.css(".duration::text").get())
            dates_raw.append(todate.strftime("%B %d, %Y"))
            dates.append(todate.strftime("%Y-%m-%d"))
            rankeds.append(i)
            i+=1
        
        edition= []
        for item in zip(titles, dates_raw, dates, urls, durations, rankeds):
            scraped_info = {
                'title': item[0],
                'date_raw': item[1],
                'date': item[2],
                'url': response.request.url,
                'news_url': item[3],
                'duration': item[4],
                'ranked': item[5],
                'epoch': time.time(),
                'language': "FR",
                'source': "RTS"
            }
            edition.append(scraped_info)
        
        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/FR/RTS"
        scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
        with open(scraped_data_filepath, "w") as f:
            json.dump(edition, f, indent= 4, ensure_ascii=False)
            f.write("\n")