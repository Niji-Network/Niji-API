from bson import ObjectId


def fix_mongo_document(doc: dict) -> dict:
    """
    Recursively convert MongoDB ObjectId(s) to strings in a given document.

    This function checks if the input dictionary contains an '_id' field
    whose value is an ObjectId and converts it to a string. This makes the document
    JSON serializable.

    Args:
        doc (dict): The MongoDB document to process.

    Returns:
        dict: The document with the '_id' converted to a string.
    """
    if doc and "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc