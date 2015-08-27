import shelve



class CourseScraperPipeline(object):
    def process_item(self, item, spider):
        return item


class PicklePipeline(object):

    def __init__(self):
        self.courses = { }


    def process_item(self, item, spider):
        key = item['code'].encode('ascii')
        item_dict = {  # iter through item.keys instead of doing this manually
            'study_type': item['study_type'],
            'category': item['category'],
            'course_url': item['course_url'],
            'level': item['level'],
            'half': item['half'],
            'credits': item['credits'],
            'code': item['code'],
            'id': item['id'],
            'title': item['title'],
            'timetable_json_url': item['timetable_json_url'],
            'timetable_json': item['timetable_json'],
        }

        self.courses[key] = item_dict


    def close_spider(self, spider):
        shelf = shelve.open('courses.db')

        for k,v in self.courses.iteritems():
            shelf[k] = v

        print("=============+_+_+_+_+_==============")
        shelf.close()




