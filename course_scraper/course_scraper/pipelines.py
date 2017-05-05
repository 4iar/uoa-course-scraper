import json


class JSONPipeline(object):

    def __init__(self):
        self.courses = {}
        self.filename = 'courses.json'

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

        try:
            item_dict['timetable_json_lectures_only'] = [l for l in item['timetable_json']['events']
                                                         if l['typeShort'] == 'LEC']
        except (KeyError, ValueError):  # handles courses with no timetable (e.g. distance learning)
            item_dict['timetable_json_lectures_only'] = None

        self.courses[key] = item_dict

    def close_spider(self, spider):
        fp = open(self.filename, 'w')
        fp.write(json.dumps(self.courses))
        fp.close()
