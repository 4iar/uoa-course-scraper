from scrapy.item import Item, Field


class Course(Item):
    category = Field()
    study_type = Field()
    course_url = Field()
    level = Field()
    half = Field()
    credits = Field()
    code = Field()
    id = Field()
    title = Field()
    timetable_json_url = Field()
    timetable_json = Field()














