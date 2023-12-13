#!/usr/bin/env python

import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
from datetime import datetime
import time
from os import path
import json

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"https://www.zdf.de/nachrichten/heute-19-uhr/"
NINETEEN_ENDING = "-heute-sendung-19-uhr-100.html"



#QUESTO SCRIPT VA USATO SOLO DOPO (CIRCA) LE 20, PRIMA L'EDIZIONE NON VIENE TROVATA NEL SITO CAUSANDO UN CRASH (nello script "letsScrape" è tutto controllato)

class ZdfgetSpider(scrapy.Spider):
    name = 'zdfGet'
    today= datetime.today().strftime("%y%m%d")
    allowed_domains = [BASE_URL]
    start_urls = [f"{BASE_URL}{today}{NINETEEN_ENDING}"]

    def parse(self, response):
        box = response.css(".details")
        box_titles= box.css(".item-description::text").get()
        titles= box_titles.split(";")
        
        box_dates= box.css(".teaser-info::text").getall()
        date= box_dates[1]
        
        url= response.url
        
        ranks= []
        contents= []
        for i in range(0, len(titles)):
            returning= ""
            tcont= titles[i].split("-")
            if len(tcont) > 1:
                tcont= tcont[1:len(tcont)]
                for cont in tcont:
                    returning+= cont + ""
            contents.append(returning)
            ranks.append(i)
        
        
        edition= []
        for item in zip(titles, contents, ranks):
            scraped_info = {
                'title': item[0].replace("\n","").strip(),
                'date_raw': datetime.strptime(date, "%d.%m.%Y").strftime("%B %d, %Y"),
                'date': datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d"),
                'url': response.request.url,
                'news_url': url,
                'content': item[1],
                'ranked': item[2],
                'placed': "First_Page",
                'epoch': time.time(),
                'langauge': "DE",
                'source': "Zdf"
            }
            edition.append(scraped_info)

        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/DE/Zdf"
        scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
        with open(scraped_data_filepath, "w") as f:
            json.dump(edition, f, indent=4, ensure_ascii=False)
            f.write("\n")
         
