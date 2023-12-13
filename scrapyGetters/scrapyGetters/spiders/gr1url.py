#!/usr/bin/env python

import scrapy
import re

#SCRIPT NON FUNZIONANTE
#CAUSA RIMOZIONE DESCRIZIONE EDIZIONI DEL GR1


class Gr1urlSpider(scrapy.Spider):
    name = 'gr1url'
    allowed_domains = ['www.raiplayradio.it/programmi/']
    start_urls = ['https://www.raiplayradio.it/programmi/gr1/archivio/puntate/']

    def parse(self, response):
        base_url= "https://www.raiplayradio.it"
        boxes= response.css(".listaAudio")
        boxes= boxes.css("h3")
        for box in boxes:
            title= box.css("a::text").get()
            to_search= "ore 8"
            print(title)
            if re.search(to_search, title):
                print(title)
                f = open("gr1urls.txt", "w")
                f.write(base_url + box.css("a::attr(href)").get() + "\n")
                f.close()

