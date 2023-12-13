#!/usr/bin/env python

import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
from datetime import datetime
import time
from os import path
import json

#SCRIPT NON FUNZIONANTE
#CAUSA RIMOZIONE DESCRIZIONE EDIZIONI DEL GR1

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"www.raiplayradio.it"


class Gr1getSpider(scrapy.Spider):
    f=open("gr1urls.txt", "r+")
    toGetUrls= f.read()
    f.close()
    toGetUrls = toGetUrls.split("\n")
    name = 'gr1Get'
    allowed_domains = [BASE_URL]
    start_urls = toGetUrls

    def removingNewLines(self, titles):
        while True:
            try:
                titles.remove("\n")
            except:
                break       
        titles= titles[0:len(titles)-1]
        return titles
    
    def gettingContents(self, titles):
        contents= []
        for i in range(0, len(titles)):
            toApp= ""
            con= titles[i].split(".")
            titles[i]= con[0] + "."
            con= con[1:len(con)]
            for c in con:
                toApp+= c + ". "
            contents.append(toApp)
        return (titles, contents)

    def formatTitle(self, title):
        return title.replace("\r", "").replace("\n", "").replace("\t", "").strip()

    def parse(self, response):
        box= response.css(".descriptionProgramma")
        timebox= box.css("ul").css("li").css("span::text").get()
        date= datetime.strptime(timebox, "%d/%m/%Y")
        d_raw= date.strftime("%B %d, %Y")
        d_real= date.strftime("%Y-%m-%d")
        url= response.url
        titles= box.css(".aodHtmlDescription::text").getall()
        
        titles = self.removingNewLines(titles)
        
        (titles, contents) = self.gettingContents(titles)
              
        i= 0
        edition= []
        for item in zip(titles, contents):
            if self.formatTitle(item[0]) == ".":
                continue
            scraped_info = {
                'title': self.formatTitle(item[0]),
                'date_raw': d_raw,
                'date': d_real,
                'url': response.request.url,
                'news_url': url,
                'content': item[1],
                'ranked': i,
                'placed': "First_Page",
                'epoch': time.time(),
                'language': "IT",
                'source': "GR1"
            }
            edition.append(scraped_info)
            i+=1
    
        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/IT/GR1"
        scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
        with open(scraped_data_filepath, "w") as f:
            json.dump(edition, f, indent=4, ensure_ascii=False)
            f.write("\n")