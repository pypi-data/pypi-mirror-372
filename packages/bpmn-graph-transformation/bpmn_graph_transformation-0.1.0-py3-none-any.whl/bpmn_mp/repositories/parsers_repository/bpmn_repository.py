from datetime import datetime
from app.infrastructure.db.mongo_client import get_collection
from app.utils.logger import get_logger
from app.utils.exceptions.db_exceptions import DatabaseException
from bson.objectid import ObjectId

logger = get_logger(__name__)
collection = get_collection("parsed_bpmn")

def save_parsed_bpmn_to_mongo(filename: str, parsed_json: dict, format_name: str):
    doc = {
        "filename": filename,
        "source_format": format_name,
        "uploaded_at": datetime.utcnow(),
        "parsed_data": parsed_json
    }
    try:
        result = collection.insert_one(doc)
        logger.info(f"Parsed BPMN inserted with id: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Failed to insert parsed BPMN: {e}")
        raise DatabaseException(str(e))

def get_parsed_bpmn_by_id(mongo_id: str):
    try:
        doc = collection.find_one({"_id": ObjectId(mongo_id)})
        if doc:
            logger.info(f"Found BPMN with id: {mongo_id}")
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        else:
            logger.warning(f"No BPMN found with id: {mongo_id}")
        return doc
    except Exception as e:
        logger.error(f"Failed to get BPMN: {e}")
        raise DatabaseException(str(e))

def delete_bpmn_by_id(mongo_id: str) -> int:
    try:
        result = collection.delete_one({"_id": ObjectId(mongo_id)})
        if result.deleted_count == 0:
            logger.warning(f"No BPMN document found with id: {mongo_id}")
        else:
            logger.info(f"BPMN document with id {mongo_id} deleted")
        return result.deleted_count
    except Exception as e:
        logger.error(f"Failed to delete BPMN: {e}")
        raise DatabaseException(str(e))