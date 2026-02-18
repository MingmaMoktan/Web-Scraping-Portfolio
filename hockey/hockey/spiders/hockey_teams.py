import scrapy
import requests


class HockeyTeamsSpider(scrapy.Spider):
    name = "hockey_teams"
    allowed_domains = ["scrapethissite.com"]

    def start_requests(self):
        for pg_no in range(1, 25):
            yield scrapy.Request(url=f'https://www.scrapethissite.com/pages/forms/?page_num={pg_no}', callback=self.parse)

    def parse(self, response):
        blocks = response.xpath("//tr[@class='team']")
        for each_block in blocks:
            name = each_block.xpath(".//td[@class='name']/text()").get()
            year = each_block.xpath(".//td[@class='year']/text()").get()
            wins = each_block.xpath(".//td[@class='wins']/text()").get()
            losses = each_block.xpath(".//td[@class='losses']/text()").get()
        
            yield {
                'Team Name': name.replace("\n", '').replace(" ", ""),
                'Year': year.replace("\n", '').replace(" ", ""),
                'wins': wins.replace("\n", '').replace(" ", ""),
                'losses': losses.replace("\n", '').replace(" ", "")
            }