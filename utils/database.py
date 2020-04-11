import os
from typing import Dict, List
import pymongo


# 'social-network'

class Database:
    URI = os.environ.get('DATABASE_URI') or str(os.environ.get("HOST")) + str(os.environ.get("MONGODB_DEV_NAME"))
    CLIENT = pymongo.MongoClient(URI)
    DATABASE = CLIENT.get_default_database()

    @staticmethod
    def insert(collection: str, data: Dict, meta: List) -> None:
        Database.DATABASE[collection].insert_one(data)
        for index in meta:
            Database.DATABASE[collection].create_index([index])

    @staticmethod
    def find(collection: str, query: Dict) -> pymongo.cursor:
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def count_record(collection: str, query: Dict):
        return Database.DATABASE[collection].count_documents(query)

    @staticmethod
    def find_one(collection: str, query: Dict) -> Dict:
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update(collection: str, query: Dict, data: Dict) -> None:
        Database.DATABASE[collection].update_one(query, data)
        Database.DATABASE[collection].reindex()

    @staticmethod
    def remove(collection: str, query: Dict) -> Dict:
        return Database.DATABASE[collection].remove(query)
