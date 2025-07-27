from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.MONGODB_URL, uuidRepresentation="standard")

db = client[settings.MONGODB_DB_NAME]


def get_collection(collection_name: str):
    return db[collection_name]
