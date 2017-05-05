import json


class JSONPipeline(object):

    def __init__(self):
        self.courses = {}
        self.filename = 'courses.json'

    def process_item(self, item, spider):
        course = item['code']

        keys = [
            'study_type',
            'category',
            'course_url',
            'level',
            'half',
            'credits',
            'code',
            'id',
            'title',
            'timetable_json_url',
            'timetable_json'
        ]

        item_extracted = {}
        for k in keys:
            item_extracted[k] = item[k]

        # There are multiple types of events such as labs (LAB), seminars (SEM), etc.
        # -> Extract only the lecture events (LEC) since these are most relevant for clash checking.
        try:
            item_extracted['timetable_json_lectures_only'] = [l for l in item['timetable_json']['events']
                                                              if l['typeShort'] == 'LEC']
        except (KeyError, ValueError):
            # Some courses have no timetable (e.g. distance learning courses), so handle these appropriately
            item_extracted['timetable_json_lectures_only'] = None

        self.courses[course] = item_extracted

    def close_spider(self, spider):
        """
        Dump the results to a json file

        Note:
            There are only ~1200 courses which takes up minimal ram so in this case it is faster to store the data
            in memory and write once at the end (rather than appending a new row for each item).

            If there were far more courses it would be more efficient to write on each item rather than
            storing in memory.
        """
        fp = open(self.filename, 'w')
        fp.write(json.dumps(self.courses))
        fp.close()
