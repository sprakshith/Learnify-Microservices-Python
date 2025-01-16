from bson.json_util import dumps
from service import user_service
from database_util.connector import get_database
from database_util.connector import create_object_id


def create_course(course):
    db = get_database()
    response = db.courses.insert_one(course).inserted_id
    return response.__str__()


def get_all_courses():
    db = get_database()
    response = db.courses.find()

    courses = []

    for course in list(response):
        course = {
            "id": str(course["_id"]),
            "title": course["title"],
            "description": course["description"],
            "teacher_id": course["teacher_id"],
            "updated_date": course["updated_date"].strftime("%Y-%m-%d")
        }

        courses.append(course)

    return dumps(courses)


def get_course(course_id):
    db = get_database()

    response = db.courses.find_one({"_id": create_object_id(course_id)})

    if response:
        course = {
            "id": str(response["_id"]),
            "title": response["title"],
            "description": response["description"],
            "teacher_id": response["teacher_id"],
            "updated_date": response["updated_date"].strftime("%Y-%m-%d"),
            "reviews": [],
            "materials": []
        }

        return dumps(course)
    else:
        raise Exception("Course not found!")


def get_enrolled_courses(jwt):
    enrolled_courses_ids = user_service.get_enrolled_courses(jwt)

    db = get_database()

    courses = []

    for course_id in enrolled_courses_ids:
        response = db.courses.find_one({"_id": create_object_id(course_id)})

        if response:
            course = {
                "id": str(response["_id"]),
                "title": response["title"],
                "description": response["description"],
                "teacher_id": response["teacher_id"],
                "updated_date": response["updated_date"].strftime("%Y-%m-%d")
            }

            courses.append(course)

    return dumps(courses)


def get_created_courses(teacher_id):

    db = get_database()

    response = db.courses.find({"teacher_id": teacher_id})

    courses = []

    for course in list(response):
        course = {
            "id": str(course["_id"]),
            "title": course["title"],
            "description": course["description"],
            "teacher_id": course["teacher_id"],
            "updated_date": course["updated_date"].strftime("%Y-%m-%d")
        }

        courses.append(course)

    return dumps(courses)


def get_teacher_id(course_id):
    db = get_database()
    response = db.courses.find_one({"_id": create_object_id(course_id)})
    return response["teacher_id"]
