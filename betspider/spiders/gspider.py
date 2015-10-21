import scrapy
from betspider.items import Bet
from scrapy.http.request import Request
from scrapy import Selector
from scrapy import Spider

class betspider(Spider):
    name = "gspider"
    allowed_domains = ["thegreek.com"]
    start_urls = []

    def start_requests(self):
        yield scrapy.Request("http://www.thegreek.com/sportsbook/betting-lines/soccer",
        cookies={'odds':'Decimal'}, callback=self.parse)

    def parse(self, response):
        item = Bet()
        item['bookmaker'] = 'TheGreek'
        item['sport'] = 'Soccer'
        item['eventDate'] = '23'
        item['moneyLine'] = {}
        item['totals'] = {}
        item['spreads'] = {}

        
        
        leagues = Selector(response).xpath('//div[@class="table-container"]')
        for league in leagues:
            item['league'] = league.xpath('h4/text()').extract()[0].strip()
            lines = leagues.xpath('div[@class="lines"]') 
            for line in lines:
                item['homeTeam'] = line.xpath('ul/li[@class="name"]/a/text()').extract()[0].strip()
                item['awayTeam'] = line.xpath('ul/li[@class="name"]/a/text()').extract()[1].strip()
                item['moneyLine']['home'] = line.xpath('ul/li[@id="ml"]/a/text()').extract()[0].strip()
                item['moneyLine']['draw'] = line.xpath('ul/li[@id="ml"]/a/text()').extract()[1].strip()
                item['moneyLine']['away'] = line.xpath('ul/li[@id="ml"]/a/text()').extract()[2].strip()
                item['totals']['points'] = line.xpath('ul/li[@id="gt"]/a/text()').extract()[0].strip().encode("utf8")
                item['totals']['over'] = line.xpath('ul/li[@id="gt"]/a/text()').extract()[1].strip()
                item['totals']['under'] = line.xpath('ul/li[@id="gt"]/a/text()').extract()[3].strip()
                item['spreads']['hdp'] = line.xpath('ul/li[@id="spread_home"]/a/text()').extract()[0].strip().encode("utf8")
                item['spreads']['home'] = line.xpath('ul/li[@id="spread_home"]/a/text()').extract()[1].strip()
                item['spreads']['away'] = line.xpath('ul/li[@id="spread_away"]/a/text()').extract()[1].strip()
                yield item
