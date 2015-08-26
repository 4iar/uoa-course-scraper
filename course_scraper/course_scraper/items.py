from scrapy.item import Item, Field



class StudyType(Item):
    """Method of study (UG, PG, DL)"""
    study_type = Field()

class Category(StudyType):
    category = Field()

class Module(Category):
    level = Field()
    half = Field()
    credits = Field()
    code = Field()
    id = Field()














