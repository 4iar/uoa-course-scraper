from scrapy import Spider
from scrapy.selector import Selector

from course_scraper.items import Course, Category


class CourseSpider(Spider):
    name = "course"
    allowed_domains = ["aberdeen.ac.uk", "abdn.ac.uk"]
    start_urls = ["https://www.abdn.ac.uk/registry/courses/undergraduate"]

    def parse(self, response):
        #categories = Selector(response).xpath('//html/body/div[5]/div[12]/div[2]/div/div[2]/div[2]/a')
        categories = Selector(response).xpath('//html/body/div[5]/div[*]/div[*]/div')
        for category in categories:
            item = Category()
            item['category'] = category.xpath('div[1]/h2/text()').extract()[0]
            item['category_url'] = category.xpath('div[2]/div[2]/a/@href').extract()[0]

            yield [Request(url=category_address,callback=self.get_course_information, meta={'item': item}]

    def parse_categories(self, response):
        item = response.meta['item']
        item['course_url'] = category.xpath('//html/body/div[5]/div[*]/div[*]/div/div[3]/div[2]/a/@href')

        for course in courses:
            item = response.meta['item']
            item['course_url'] = course

        return [Request("http://www.example.com/lin2.cpp", callback=self.parseDescription2, meta={'item': item})]
