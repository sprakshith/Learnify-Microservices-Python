import json
import datetime
from flask import Flask, request
from service import user_service, course_service, material_service, review_service


app = Flask(__name__)


@app.route('/api/v1/courses', methods=['POST'])
def create_course():
    body = request.json

    token = request.headers['Authorization']

    user = user_service.get_user_details(token)

    if not user:
        return "Unauthorized", 401

    if user['role'] != 'TEACHER':
        return "Only teachers can create courses", 403

    course = {
        "title": body['title'],
        "description": body['description'],
        "teacher_id": user['id'],
        "created_date": datetime.datetime.now(tz=datetime.timezone.utc),
        "updated_date": datetime.datetime.now(tz=datetime.timezone.utc)
    }

    try:
        return f"Course with ID: {course_service.create_course(course)}, successfully created!", 201
    except Exception as e:
        return str(e), 500


@app.route('/api/v1/courses', methods=['GET'])
def get_courses():
    try:
        return course_service.get_all_courses()
    except Exception as e:
        return str(e), 500


@app.route('/api/v1/courses/<string:course_id>', methods=['GET'])
def get_course(course_id):
    # FIXME: This should also return reviews and materials properly.
    try:
        return course_service.get_course(course_id), 200
    except Exception as e:
        return str(e), 500


@app.route('/api/v1/courses/my-courses', methods=['GET'])
def get_my_courses():
    token = request.headers['Authorization']

    user_details = user_service.get_user_details(token)

    if user_details['role'] == 'STUDENT':
        return course_service.get_enrolled_courses(token), 200
    elif user_details['role'] == 'TEACHER':
        return course_service.get_created_courses(user_details['id']), 200
    else:
        return "Unauthorized", 401


@app.route('/api/v1/courses/<string:course_id>/get-teacher-id', methods=['GET'])
def get_teacher_id(course_id):
    try:
        return str(course_service.get_teacher_id(course_id)), 200
    except Exception as e:
        return str(e), 500


@app.route('/api/v1/courses/<string:course_id>/materials/upload', methods=['POST'])
def upload_material(course_id):
    token = request.headers['Authorization']

    user = user_service.get_user_details(token)

    if not user:
        return "Unauthorized", 401

    if user['role'] != 'TEACHER':
        return "Only teachers can upload materials!", 403

    try:
        return material_service.upload_material(user['id'], course_id, request), 201
    except PermissionError as e:
        return str(e), 403
    except Exception as e:
        return str(e), 500


@app.route('/api/v1/courses/<string:course_id>/materials', methods=['GET'])
def get_materials(course_id):
    try:
        return material_service.get_materials_list(course_id), 200
    except Exception as e:
        return str(e), 500


@app.route('/api/v1/courses/<string:course_id>/materials/download/<string:material_id>', methods=['GET'])
def download_material(course_id, material_id):
    allowed_courses, _ = get_my_courses()
    allowed_courses = [course['id'] for course in json.loads(allowed_courses)]

    if course_id not in allowed_courses:
        return "Unauthorized", 401

    try:
        return material_service.download_material(course_id, material_id), 200
    except Exception as e:
        return str(e), 500


@app.route('/api/v1/courses/<string:course_id>/reviews', methods=['POST'])
def create_review(course_id):
    body = request.json

    token = request.headers['Authorization']

    user = user_service.get_user_details(token)

    if not user:
        return "Unauthorized", 401

    if user['role'] != 'STUDENT':
        return "Only students can add review!", 403

    course = {
        "course_id": course_id,
        "student_id": user['id'],
        "rating": body['rating'],
        "comment": body['comment'],
        "created_date": datetime.datetime.now(tz=datetime.timezone.utc),
        "updated_date": datetime.datetime.now(tz=datetime.timezone.utc)
    }

    try:
        return f"Review with ID: {review_service.create_review(course)}, successfully created!", 201
    except Exception as e:
        return str(e), 500


@app.route('/api/v1/courses/<string:course_id>/reviews', methods=['GET'])
def get_reviews(course_id):
    return review_service.get_reviews_by_course(course_id), 200


@app.route('/api/v1/courses/<string:course_id>/reviews/<string:review_id>', methods=['PUT'])
def update_review(course_id, review_id):
    body = request.json

    token = request.headers['Authorization']

    user = user_service.get_user_details(token)

    if not user:
        return "Unauthorized", 401

    if user['role'] != 'STUDENT':
        return "Only students can access this!", 403

    try:
        return review_service.update_review(review_id, body, user['id']), 200
    except PermissionError as e:
        return str(e), 403
    except Exception as e:
        return str(e), 500


@app.route('/api/v1/courses/<string:course_id>/reviews/<string:review_id>', methods=['DELETE'])
def delete_review(course_id, review_id):
    token = request.headers['Authorization']

    user = user_service.get_user_details(token)

    if not user:
        return "Unauthorized", 401

    if user['role'] != 'STUDENT':
        return "Only students can access this!", 403

    try:
        return review_service.delete_review(review_id, user['id']), 200
    except PermissionError as e:
        return str(e), 403
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
