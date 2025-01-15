import os
import jwt
import hmac
import hashlib
import datetime


def hash_password(password):
    return hmac.new(
        os.environ.get('SECRET_KEY').encode(),
        password.encode(),
        hashlib.sha256
    ).hexdigest()


def create_jwt(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc),
            "admin": authz
        },
        secret,
        algorithm="HS256"
    )
