from bson import ObjectId, Binary, DBRef, Regex, Code, Timestamp, Decimal128
from json import JSONEncoder
from datetime import datetime


class MongoJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return {"$date": obj.isoformat()}
        elif isinstance(obj, ObjectId):
            return {"$oid": str(obj)}
        elif isinstance(obj, Binary):
            return {"$binary": obj.decode("utf-8", "ignore")}
        elif isinstance(obj, DBRef):
            return {
                "$dbRef": {
                    "$ref": obj.collection,
                    "$id": str(obj.id),
                    "$db": obj.database,
                }
            }
        elif isinstance(obj, Regex):
            return {"$regex": obj.pattern, "$options": obj.flags}
        elif isinstance(obj, Code):
            return {"$code": str(obj)}
        elif isinstance(obj, Timestamp):
            return {"$timestamp": {"t": obj.time, "i": obj.inc}}
        elif isinstance(obj, Decimal128):
            return {"$numberDecimal": str(obj)}
        # Add more types if necessary
        return JSONEncoder.default(self, obj)
