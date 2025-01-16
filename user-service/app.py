import os
import jwt
from dotenv import load_dotenv
from flask import Flask, request
from sqlalchemy.exc import IntegrityError
from service.utils import hash_password, create_jwt
from model.models import User, Enrollment, get_session

load_dotenv()

app = Flask(__name__)


@app.route('/api/v1/authentication/register', methods=['POST'])
def register():
    data = request.json

    user = User(
        first_name=data['firstName'],
        last_name=data['lastName'],
        email=data['email'],
        password=hash_password(data['password']),
        role=data['role']
    )

    session = get_session()

    session.add(user)

    session.commit()

    return "User created successfully", 201


@app.route('/api/v1/authentication/authenticate', methods=['POST'])
def authenticate():
    body = request.json

    email = body['email']
    password = body['password']

    session = get_session()

    user = session.query(User).filter_by(email=email).first()

    if user and user.password == hash_password(password):
        return {"token": create_jwt(email, os.environ.get("JWT_SECRET"), user.role == "ADMIN")}, 200

    return "Invalid Credentials!", 401


@app.route("/api/v1/authentication/validate", methods=["GET"])
def validate():
    encode_jwt = request.headers["Authorization"]

    if not encode_jwt:
        return "Missing JWT!", 401

    encode_jwt = encode_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encode_jwt,
            os.environ.get("JWT_SECRET"),
            algorithms=["HS256"]
        )

        return decoded, 200
    except Exception as e:
        print(f"Exception: {e}")

    return "Invalid Token!", 401


def has_role(role):
    user_details, status = validate()

    if status != 200:
        return {"result": False}, 401

    session = get_session()

    user = session.query(User).filter_by(email=user_details['username']).first()

    if user and user.role.value == role:
        return {"result": True}, 200
    else:
        return {"result": False}, 401


@app.route("/api/v1/users/is-admin", methods=["GET"])
def is_admin():
    return has_role("ADMIN")


@app.route("/api/v1/users/is-teacher", methods=["GET"])
def is_teacher():
    return has_role("TEACHER")


@app.route("/api/v1/users/is-student", methods=["GET"])
def is_student():
    return has_role("STUDENT")


@app.route("/api/v1/users/get-user-details", methods=["GET"])
def get_user_details():
    user_details, status = validate()

    if status != 200:
        return "Invalid Token!", 401

    session = get_session()

    user = session.query(User).filter_by(email=user_details['username']).first()

    return {
        "id": user.id,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "email": user.email,
        "role": user.role.value
    }, 200


@app.route("/api/v1/users/enrol/<string:course_id>", methods=["POST"])
def enrol(course_id):
    user_details, status = get_user_details()

    if status != 200:
        return "Invalid Token!", 401

    if not user_details['role'] == "STUDENT":
        return "Only students can enrol!", 401

    try:
        session = get_session()

        enrollment = Enrollment(
            course_id=course_id,
            student_id=user_details['id']
        )

        session.add(enrollment)

        session.commit()
    except IntegrityError as e:
        return f"User already enrolled!\n\n{e}", 400

    return "User enrolled successfully!", 200


@app.route("/api/v1/users/get-enrolled-courses", methods=["GET"])
def get_enrolled_courses():
    user_details, status = get_user_details()

    if status != 200:
        return "Invalid Token!", 401

    if not user_details['role'] == "STUDENT":
        return "Only students have access to this!", 401

    session = get_session()

    enrolled_courses = session.query(Enrollment).filter_by(student_id=user_details['id']).all()

    return [enrollment.course_id for enrollment in enrolled_courses], 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
