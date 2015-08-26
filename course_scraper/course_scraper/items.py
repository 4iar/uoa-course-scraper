from scrapy.item import Item, Field



class StudyType(Item):
    """Method of study (UG, PG, DL)"""
    study_type = "UG"

class Category(StudyType):
    category = Field()
    category_url = Field()

class Course(Category):
    course_url = Field()
    level = Field()
    half = Field()
    credits = Field()
    code = Field()
    id = Field()
    title = Field()
    timetable_json_url = Field()
    timetable_json = Field()














