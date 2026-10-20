from __future__ import annotations
from pymongo import MongoClient, ASCENDING
from .config import MONGO_URI, MONGO_DB

def db():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    return client[MONGO_DB]

def replace_collection(name, records):
    collection = db()[name]
    collection.delete_many({})
    if records:
        collection.insert_many(records)
    return len(records)

def ensure_indexes():
    database = db()
    database.pollution.create_index([("date", ASCENDING), ("site_id", ASCENDING)])
    database.weather.create_index("date", unique=True)
    database.daily_analysis.create_index("date", unique=True)

def monthly_aggregation():
    return list(db().daily_analysis.aggregate([
        {"$group":{"_id":{"$month":"$date"},"pm25":{"$avg":"$pm25_mean"},"max_pm25":{"$max":"$pm25_max"},"days":{"$sum":1}}},
        {"$sort":{"_id":1}}
    ]))

def county_aggregation():
    return list(db().pollution.aggregate([
        {"$group":{"_id":"$county","pm25":{"$avg":"$pm25"},"observations":{"$sum":1}}},
        {"$sort":{"pm25":-1}}
    ]))

