from datetime import datetime, timezone
from bson import ObjectId


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def serialize_doc(doc: dict) -> dict:
    out = dict(doc)
    if "_id" in out:
        out["id"] = str(out.pop("_id"))
    return out


def parse_object_id(value: str) -> ObjectId:
    return ObjectId(value)
