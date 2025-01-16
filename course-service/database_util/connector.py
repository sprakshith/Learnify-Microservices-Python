import os
import gridfs
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId

load_dotenv()

MONGO_USERNAME = os.environ.get("MONGO_USERNAME")
MONGO_PW = os.environ.get("MONGO_PW")
MONGO_HOST = os.environ.get("MONGO_HOST")
MONGO_PORT = os.environ.get("MONGO_PORT")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE")


def get_database():
    db_url = f"mongodb://{MONGO_USERNAME}:{MONGO_PW}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}?authSource=admin"
    client = MongoClient(db_url)

    if MONGO_DATABASE not in client.list_database_names():
        client[MONGO_DATABASE].create_collection("dummy_collection")
        client[MONGO_DATABASE].drop_collection("dummy_collection")

    collections = ["courses", "reviews", "materials"]
    for collection in collections:
        if collection not in client[MONGO_DATABASE].list_collection_names():
            client[MONGO_DATABASE].create_collection(collection)

    return client[MONGO_DATABASE]


def get_gridfs():
    db = get_database()
    return gridfs.GridFS(db)


def create_object_id(_id):
    return ObjectId(_id)
