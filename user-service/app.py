import os
import jwt
from dotenv import load_dotenv
from flask import Flask, request
from model.models import User, get_session
from service.utils import hash_password, create_jwt

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
