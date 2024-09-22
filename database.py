# database.py
from pymongo import MongoClient, errors
from typing import Any, Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDB:
    _instance = None 

    def __new__(cls, uri: str, database_name: str):
        if cls._instance is None:
            try:
                cls._instance = super(MongoDB, cls).__new__(cls)
                cls._instance.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
                cls._instance.db = cls._instance.client[database_name]
                cls._instance.client.admin.command('ping')
                logger.info(f"Connected to MongoDB database: {database_name}")
            except errors.ServerSelectionTimeoutError as e:
                logger.error(f"Unable to connect to the database: {e}")
                raise ConnectionError("Database connection failed.")
        return cls._instance

    def insert_one(self, collection: str, document: Dict[str, Any]) -> Any:
        """Insert a document into a collection."""
        try:
            result = self.db[collection].insert_one(document)
            logger.info(f"Document inserted into {collection}: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to insert document into {collection}: {e}")
            raise RuntimeError(f"Failed to insert document: {e}")

    def get_all(self, collection: str) -> List[Dict[str, Any]]:
        """Retrieve all documents from a collection"""
        try:
            cursor = self.db[collection].find()
            documents = list(cursor)
            logger.info(f"Retrieved {len(documents)} documents from {collection}")
            return documents
        except Exception as e:
            logger.error(f"Failed to retrieve documents from {collection}: {e}")
            raise RuntimeError(f"Failed to retrieve documents: {e}")

    def find_one(self, collection: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Find a single document in a collection."""
        try:
            result = self.db[collection].find_one(query)
            if result:
                logger.info(f"Document found in {collection} with query: {query}")
            else:
                logger.warning(f"No document found in {collection} with query: {query}")
            return result
        except Exception as e:
            logger.error(f"Failed to find document in {collection}: {e}")
            raise RuntimeError(f"Failed to find document: {e}")

    def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete a single document from a collection."""
        try:
            result = self.db[collection].delete_one(query)
            if result.deleted_count > 0:
                logger.info(f"Document deleted from {collection} with query: {query}")
            else:
                logger.warning(f"No document found to delete in {collection} with query: {query}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete document from {collection}: {e}")
            raise RuntimeError(f"Failed to delete document: {e}")

    def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document in a collection."""
        try:
            result = self.db[collection].update_one(query, {"$set": update})
            if result.matched_count > 0:
                if result.modified_count > 0:
                    logger.info(f"Document updated in {collection} with query: {query}")
                else:
                    logger.warning(f"Document found but not modified in {collection}: {query}")
            else:
                logger.warning(f"No document found to update in {collection}: {query}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update document in {collection}: {e}")
            raise RuntimeError(f"Failed to update document: {e}")
