from scrapy import Spider, Request, FormRequest
from scrapy.selector import Selector
import json

from course_scraper.items import Course


class CourseSpider(Spider):
    name = "course"
    allowed_domains = ["aberdeen.ac.uk", "abdn.ac.uk"]
    start_urls = ["https://www.abdn.ac.uk/registry/courses/undergraduate"]

    def parse(self, response):
        category_urls = Selector(response).xpath('//html/body/div[5]/div[*]/div[*]/div/div[2]/div[2]/a/@href').extract()

        for category_url in category_urls:
            yield Request(url=category_url,callback=self.parse_categories)

    def parse_categories(self, response):
        course_urls = response.xpath('//html/body/div[5]/div[*]/div[*]/div/div[3]/div[2]/a/@href').extract()

        for course_url in course_urls:
            yield Request(url=course_url,callback=self.parse_courses)
            
    def parse_courses(self, response):

        item = Course()
        item['study_type'] = "UG"
        item['category'] = response.xpath('/html/body/div[3]/div/ol/li[5]/a/text()').extract()[0]
        item['title'] = response.xpath('//html/body/div[3]/div/ol/li[6]/text()').extract()[0].encode('ascii')
        item['course_url'] = response.url
        item['level'] = int(response.xpath('//*[@id="overview"]/div[2]/div[2]/div/table/tbody/tr[1]/td[2]/text()').extract()[0])
        item['code'] = response.xpath('//*[@id="course-1"]/@value').extract()[0].encode('ascii')
        item['credits'] = float(response.xpath('//*[@id="overview"]/div[2]/div[2]/div/table/tbody/tr[2]/td[2]/text()').extract()[0].split()[0])

        h = response.xpath('//*[@id="overview"]/div[2]/div[2]/div/table/tbody/tr[2]/td[1]/text()')
        if 'First' in h or 'first' in h:
            item['half'] = 1
        else:
            item['half'] = 2

        courses = {  # template form data
                     'course-1': item['code'],
                     'course-2': '',
                     'course-3': '',
                     'course-4': '',
                     'course-5': '',
                     'course-6': '',
                     'course-7': '',
                     'course-8': '',
                     'submit': 'submit'
                     }

        url = 'https://www.abdn.ac.uk/mist/apps/courseoverlay/timetable/overlays/'
        return [FormRequest(url, formdata=courses, callback=self.parse_course_timetable, meta={'item': item})]


    def parse_course_timetable(self, response):
        item = response.meta['item']
        item['id'] = int(response.xpath('//script[@type="text/javascript"]').re(r'var +courseId + = +"([0-9]+)";')[0])
        item['timetable_json_url'] = str.format("https://www.abdn.ac.uk/mist/apps/courseoverlay/timetable/fullTimetableAjax/2015-06-07%2000:00:00/2015-12-07%2000:00:00/{}/0", str(item['id']))

        return [Request(item['timetable_json_url'], callback=self.parse_timetable_json, meta={'item': item})]

    def parse_timetable_json(self, response):
        item = response.meta['item']
        item['timetable_json'] = json.loads(response.body_as_unicode())

        yield item



















