from .courses import courses

def search_by_duration(duration):
    for course in courses:
        if course.duration == duration:
            return course

    return None
   
def total_duration():
    return sum(course.duration for course in courses)
