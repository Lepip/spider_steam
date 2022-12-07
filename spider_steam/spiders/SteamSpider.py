import scrapy
from urllib.parse import urlencode
from urllib.parse import urljoin
import re
import json
from spider_steam.items import SpiderSteamItem
from bs4 import BeautifulSoup

class SteamspiderSpider(scrapy.Spider):
    argumm = 0
    def parse(self, response, **kwargs):
        for a in response.xpath('//a[@data-gpnav="item"]').extract():
            url = BeautifulSoup(a).find('a', href=True)['href']
            yield scrapy.Request(url=url, callback=self.parse_game)

    name = 'SteamSpider'
    start_urls = ['https://store.steampowered.com/search/?tags=492&category1=998', 'https://store.steampowered.com/search/?tags=29482&category1=998', 'https://store.steampowered.com/search/?tags=3871&category1=998']
    allowed_domains = ['store.steampowered.com']

    def parse_game(self, response):
        if "agecheck" in response.url:
            return
        date = int(response.xpath('//div[@class="date"]/text()').extract()[0].split()[2])
        if date < 2000:
            return
        item = SpiderSteamItem()
        item["name"] = response.xpath('//div[@id="appHubAppName"]/text()').extract()[0]
        item["category"] = response.xpath('//div[@class="blockbg"]/a[2]/text()').extract()[0]
        # item.num_reviews = int(re.sub("[^0-9]", "", response.xpath('//div[@class="summary_section"]/span[2]/text()').extract()))
        item["num_reviews"] = BeautifulSoup(response.xpath('//meta[@itemprop="reviewCount"]').extract()[0], 'html.parser').find('meta')['content']
        item["score"] = response.xpath('//div[@class="user_reviews_summary_row"and@itemprop="aggregateRating"]//span[@class="nonresponsive_hidden responsive_reviewdesc"]/text()').extract()[0].split()[1]
        item["dev"] = response.xpath('//div[@id="developers_list"]/a/text()').extract()[0]
        item["tags"] = [re.sub("\s+", "", a) for a in response.xpath('//div[@class="glance_tags popular_tags"]/a/text()').extract()]
        price_list = response.xpath('//div[@class="game_purchase_price price"or@class="discount_final_price"]/text()').extract()
        if price_list:
            item["price"] = re.sub("\s+", "", price_list[0])
        else:
            item["price"] = "Бесплатно"
        item["platforms"] = []
        platforms_html = response.xpath('//div[@class="game_area_purchase_platform"]').extract()[0]
        platforms = ["win", "mac", "linux"]
        for platform in platforms:
            if platform in platforms_html:
                item["platforms"].append(platform)
        yield item