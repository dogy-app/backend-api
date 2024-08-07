from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

from typing import Self

class Database:
    def __init__(self, connection_string: str):
        """
        Initialize the Database class with the connection string
        :param connection_string: The connection string to the MongoDB database
        """
        self.connection_string: str = connection_string
        self.__client = None
        self.database = None
        self.collection = None

    def connect_db(self) -> Self:
        """
        Connect to the MongoDB database
        """
        self.__client = MongoClient(self.connection_string, authMechanism='SCRAM-SHA-1')
        return self

    def set_collection(self, db: str, collection: str) -> Self:
        """
        Set the database and collection to be used
        :param db: The database name
        :param collection: The collection name
        """
        self.database: MongoClient = self.__client.get_database(db)
        self.collection: MongoClient = self.database.get_collection(collection)
        return self

    def insert_many(self, documents) -> Self:
        """
        Insert multiple documents into the collection
        :param documents: The documents to insert
        """
        self.collection.insert_many(documents)
        return self
