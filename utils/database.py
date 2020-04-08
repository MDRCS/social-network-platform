import os
from typing import Dict, List
import pymongo


class Database:
    URI = "mongodb://127.0.0.1:27017/social-network"
    DATABASE = pymongo.MongoClient(URI).get_default_database()

    @staticmethod
    def insert(collection: str, data: Dict, meta: List) -> None:
        Database.DATABASE[collection].insert(data)
        for index in meta:
            Database.DATABASE[collection].create_index([index])

    @staticmethod
    def find(collection: str, query: Dict) -> pymongo.cursor:
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection: str, query: Dict) -> Dict:
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update(collection: str, query: Dict, data: Dict) -> None:
        Database.DATABASE[collection].update(query, data, upsert=True)

    @staticmethod
    def remove(collection: str, query: Dict) -> Dict:
        return Database.DATABASE[collection].remove(query)
