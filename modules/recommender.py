def colleges_for_course(course, colleges):
    result = []
    for c in colleges:
        for cr in c["courses"]:
            if course.lower() in cr.lower():
                result.append(c["name"])
    return result
