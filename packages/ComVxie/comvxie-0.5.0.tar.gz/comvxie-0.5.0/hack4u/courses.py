class Course:

    def __init__(self, name, duration, link):
        self.name = name
        self.duration = duration
        self.link = link

    def __repr__(self):
        return f"Name: {self.name}, Duration: {self.duration}, Link: {self.link}"

courses = [
    Course("Introduction to linux", 13, "http:/Hack4u.com"),  
    Course("Personalization Linux", 3, "http:/Hack4u.com"),
    Course("Introduction to Hacking", 53, "http:/Hack4u.com")
]

def list_courses():
    for course in courses:
        print(course)

def search_course_by_name(name):
    for course in courses:
        if course.name == name:
            return course
    return None

