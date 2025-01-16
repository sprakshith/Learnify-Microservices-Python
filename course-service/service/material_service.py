import datetime
import mimetypes
from flask import Response
from service import user_service
from database_util.connector import get_database, get_gridfs, create_object_id\



def upload_material(teacher_id, course_id, request):

    db = get_database()

    course = db.courses.find_one({"_id": create_object_id(course_id)})

    if not course:
        raise Exception("Course not found!")

    if course['teacher_id'] != teacher_id:
        raise PermissionError("You are not the teacher of this course! You cannot upload materials!")

    grid_fs = get_gridfs()

    file_id = grid_fs.put(request.data, filename=request.files['file'].filename)

    material = {
        "course_id": course_id,
        "file_id": file_id,
        "file_name": request.files['file'].filename,
        "created_date": datetime.datetime.now(tz=datetime.timezone.utc),
        "updated_date": datetime.datetime.now(tz=datetime.timezone.utc)
    }

    response = db.materials.insert_one(material).inserted_id

    return response.__str__()


def get_materials_list(course_id):
    db = get_database()

    course = db.courses.find_one({"_id": create_object_id(course_id)})

    if not course:
        raise Exception("Course not found!")

    materials = db.materials.find({"course_id": course_id})

    materials_list = []

    for material in list(materials):
        material = {
            "id": str(material["_id"]),
            "file_name": material["file_name"],
            "created_date": material["created_date"].strftime("%Y-%m-%d")
        }

        materials_list.append(material)

    return materials_list


def download_material(course_id, material_id):
    db = get_database()

    course = db.courses.find_one({"_id": create_object_id(course_id)})

    if not course:
        raise Exception("Course not found!")

    grid_fs = get_gridfs()

    material = db.materials.find_one({"_id": create_object_id(material_id)})

    if not material:
        raise Exception("Material not found!")

    file = grid_fs.get(material['file_id'])

    content_type = mimetypes.guess_type(material['file_name'])[0] or 'application/octet-stream'

    return Response(file.read(), content_type=content_type)
