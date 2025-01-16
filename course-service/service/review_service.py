from bson.json_util import dumps
from database_util.connector import get_database
from database_util.connector import create_object_id


def create_review(review):
    db = get_database()
    response = db.reviews.insert_one(review).inserted_id
    return response.__str__()


def get_reviews_by_course(course_id):
    db = get_database()

    response = db.reviews.find({"course_id": course_id})

    reviews = []

    for review in list(response):
        review = {
            "id": str(review["_id"]),
            "user_id": review["student_id"],
            "rating": review["rating"],
            "comment": review["comment"]
        }

        reviews.append(review)

    return dumps(reviews)


def update_review(review_id, body, student_id):
    db = get_database()

    review = db.reviews.find_one({"_id": create_object_id(review_id)})

    if review["student_id"] != student_id:
        raise PermissionError("This review doesn't belong to you! You cannot update it!")

    rating = body.get("rating")
    comment = body.get("comment")

    db.reviews.update_one({"_id": create_object_id(review_id)}, {"$set": {"rating": rating, "comment": comment}})

    return "Review updated successfully!"


def delete_review(review_id, student_id):
    db = get_database()

    review = db.reviews.find_one({"_id": create_object_id(review_id)})

    if review["student_id"] != student_id:
        raise PermissionError("This review doesn't belong to you! You cannot delete it!")

    db.reviews.delete_one({"_id": create_object_id(review_id)})

    return "Review deleted successfully!"
