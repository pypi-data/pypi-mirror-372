from bson import ObjectId
from app.infrastructure.db.mongo_client import get_collection
from app.utils.logger import get_logger
from app.utils.exceptions.db_exceptions import NotFoundError, DatabaseException

logger = get_logger(__name__)
collection = get_collection("posts")

def create_post(data):
    try:
        result = collection.insert_one(data)
        logger.info(f"Post created: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Failed to create post: {e}")
        raise DatabaseException(str(e))

def get_post(post_id):
    try:
        obj_id = ObjectId(post_id)
        result = collection.find_one({"_id": obj_id})
        if not result:
            logger.warning(f"Post not found: {post_id}")
            raise NotFoundError("Post not found")
        return result
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching post: {e}")
        raise DatabaseException(str(e))

def update_post(post_id, data):
    try:
        obj_id = ObjectId(post_id)
        result = collection.update_one({"_id": obj_id}, {"$set": data})
        if result.matched_count == 0:
            logger.warning(f"Post to update not found: {post_id}")
            raise NotFoundError("Post not found")
        logger.info(f"Post updated: {post_id}")
        return result.modified_count
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error updating post: {e}")
        raise DatabaseException(str(e))

def delete_post(post_id):
    try:
        obj_id = ObjectId(post_id)
        result = collection.delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            logger.warning(f"Post to delete not found: {post_id}")
            raise NotFoundError("Post not found")
        logger.info(f"Post deleted: {post_id}")
        return result.deleted_count
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting post: {e}")
        raise DatabaseException(str(e))
