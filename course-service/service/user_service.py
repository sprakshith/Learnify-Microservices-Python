import requests


def get_user_details(jwt):
    url = "http://localhost:5002/api/v1/users/get-user-details"

    headers = {
        "Authorization": jwt
    }

    response = requests.get(url, headers=headers)

    return response.json()


def get_enrolled_courses(jwt):
    url = "http://localhost:5002/api/v1/users/get-enrolled-courses"

    headers = {
        "Authorization": jwt
    }

    response = requests.get(url, headers=headers)

    return response.json()
