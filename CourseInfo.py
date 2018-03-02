class CourseInfo(object):
    def __init__(self):
        self.base_type = ''
        self.point = ''
        self.name = ''
        self.type = ''
        self.code = ''
        self.data_array = []
        self.all_course = []

    def push_data(self):
        self.data_array.append((self.base_type, self.name, self.type, self.code, self.point))

    def push_data2(self):
        self.all_course.append((self.name, self.type, self.code, self.point))