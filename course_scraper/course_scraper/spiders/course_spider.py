from scrapy import Spider, Request, FormRequest
from scrapy.selector import Selector
import json

from course_scraper.items import Course


class CourseSpider(Spider):
    """
    Extracts undergraduate courses at UoA, providing metadata (e.g. credits, term, descriptions) and timetable data

        +-------------+     +---------+     +--------------+     +-----------+
        |  categories +---> | courses +---> | timetable id +---> | timetable |
        +-------------+     +---------+     +--------------+     +-----------+
    """
    name = "course_scraper"
    allowed_domains = ["aberdeen.ac.uk", "abdn.ac.uk"]
    start_urls = ["https://www.abdn.ac.uk/registry/courses/undergraduate"]

    def __init__(self, year=2017):
        super(CourseSpider, self).__init__()
        self.year = int(year)

    def parse(self, response):
        """
        Extracts a list of undergraduate course categories (e.g. Biology, Law, etc) and their urls

        @url https://www.abdn.ac.uk/registry/courses/undergraduate
        @returns items 0 0
        @returns requests 70 75
        """
        category_urls = Selector(response).xpath('//html/body/div[5]/div[*]/div[*]/div/div[2]/div[2]/a/@href').extract()

        for category_url in category_urls:
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        """
        Extracts the course codes within a given category.
        I.e. all the courses (e.g. SM1501, SM2501...) from Medical Sciences

        @url https://www.abdn.ac.uk/registry/courses/undergraduate/2016-2017/geography
        @returns items 0 0
        @returns requests 27 27
        """
        course_urls = response.xpath('//html/body/div[5]/div[*]/div[*]/div/div[3]/div[2]/a/@href').extract()

        for course_url in course_urls:
            yield Request(url=course_url, callback=self.parse_course)
            
    def parse_course(self, response):
        """
        Extracts the metadata and data for a given course code and sends a request for the timetable data

        @url https://www.abdn.ac.uk/registry/courses/undergraduate/2016-2017/genetics/gn3502
        @returns items 0 0
        @returns requests 1 1
        """
        item = Course()
        item['study_type'] = "UG"
        item['category'] = response.xpath('/html/body/div[3]/div/ol/li[5]/a/text()').extract()[0]
        item['title'] = response.xpath('//html/body/div[3]/div/ol/li[6]/text()').extract()[0]
        item['course_url'] = response.url
        item['level'] = int(response.xpath('//*[@id="overview"]/div[2]/div[2]/div/table/tbody/tr[1]/td[2]/text()').
                            extract()[0])
        item['code'] = response.xpath('/html/head/title/text()').extract()[0].split(':')[0]
        item['credits'] = float(response.xpath('//*[@id="overview"]/div[2]/div[2]/div/table/tbody/tr[2]/td[2]/text()').
                                extract()[0].split()[0])

        # Courses are in the first or second half of the semester. Identify which half a course is in and represent it
        # as an int for easier processing
        half_text = response.xpath('//*[@id="overview"]/div[2]/div[2]/div/table/tbody/tr[2]/td[1]/text()').extract()[0]
        if 'first' in half_text.lower():
            item['half'] = 1
        else:
            item['half'] = 2

        # Construct the form data needed to request the timetable id
        courses = {
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
        return [FormRequest(url, formdata=courses, callback=self.parse_timetable_id, meta={'item': item})]

    def parse_timetable_id(self, response):
        """
        Parse the timetable ID from the course and then send another request to get the actual timetable
        """
        item = response.meta['item']
        item['id'] = int(response.xpath('//script[@type="text/javascript"]').re(r'var +courseId + = +"([0-9]+)";')[0])
        item['timetable_json_url'] = str.format(
            "https://www.abdn.ac.uk/mist/apps/courseoverlay/timetable/fullTimetableAjax/{}-09-07%2000:00:00/{}-12-07%2000:00:00/{}/0",
            self.year - 1, self.year, str(item['id'])
        )

        return [Request(item['timetable_json_url'], callback=self.parse_timetable, meta={'item': item})]

    def parse_timetable(self, response):
        """
        Parse the timetable itself
        """
        item = response.meta['item']
        item['timetable_json'] = json.loads(response.body_as_unicode())

        yield item
