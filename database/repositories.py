from datetime import datetime, timezone
from pymongo import ReturnDocument
from database.mongo import get_db


def utcnow():
    return datetime.now(timezone.utc)


def scope_for(message):
    if message.chat.type == "private":
        return f"user:{message.from_user.id}", "private"
    return f"group:{message.chat.id}", "group"


async def next_entry_id():
    db = get_db()
    counter = await db.counters.find_one_and_update(
        {"_id": "entries"}, {"$inc": {"value": 1}}, upsert=True, return_document=ReturnDocument.AFTER
    )
    return int(counter["value"])


async def create_entry(*, scope_id, scope_type, owner_id, title, content, category, tags, status="approved"):
    db = get_db()
    entry = {
        "entry_id": await next_entry_id(),
        "scope_id": scope_id,
        "scope_type": scope_type,
        "owner_id": owner_id,
        "title": title.strip(),
        "content": content.strip(),
        "category": category.strip().lower() or "general",
        "tags": [tag.strip().lower().lstrip("#") for tag in tags if tag.strip()],
        "status": status,
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "views": 0,
    }
    await db.entries.insert_one(entry)
    return entry


async def get_entry(scope_id, entry_id, include_pending=False):
    query = {"scope_id": scope_id, "entry_id": entry_id}
    if not include_pending:
        query["status"] = "approved"
    return await get_db().entries.find_one(query)


async def search_entries(scope_id, query, page=0, page_size=5, owner_id=None):
    db = get_db()
    base = {"scope_id": scope_id, "status": "approved"}
    if owner_id is not None:
        base["owner_id"] = owner_id
    terms = query.strip()
    if terms:
        # Regex search is deliberately simple and avoids requiring Atlas Search.
        import re
        pattern = re.escape(terms)
        base["$or"] = [
            {"title": {"$regex": pattern, "$options": "i"}},
            {"content": {"$regex": pattern, "$options": "i"}},
            {"tags": {"$regex": pattern, "$options": "i"}},
            {"category": {"$regex": pattern, "$options": "i"}},
        ]
    total = await db.entries.count_documents(base)
    cursor = db.entries.find(base).sort("created_at", -1).skip(page * page_size).limit(page_size)
    return await cursor.to_list(length=page_size), total


async def update_entry(scope_id, entry_id, owner_id, title, content):
    return await get_db().entries.update_one(
        {"scope_id": scope_id, "entry_id": entry_id, "owner_id": owner_id, "status": "approved"},
        {"$set": {"title": title.strip(), "content": content.strip(), "updated_at": utcnow()}},
    )


async def delete_entry(scope_id, entry_id, owner_id=None):
    query = {"scope_id": scope_id, "entry_id": entry_id}
    if owner_id is not None:
        query["owner_id"] = owner_id
    return await get_db().entries.delete_one(query)


async def set_entry_status(scope_id, entry_id, status):
    return await get_db().entries.update_one(
        {"scope_id": scope_id, "entry_id": entry_id},
        {"$set": {"status": status, "updated_at": utcnow()}},
    )


async def get_categories(scope_id):
    values = await get_db().entries.distinct("category", {"scope_id": scope_id, "status": "approved"})
    return sorted(values)


async def stats(scope_id):
    db = get_db()
    approved = await db.entries.count_documents({"scope_id": scope_id, "status": "approved"})
    pending = await db.entries.count_documents({"scope_id": scope_id, "status": "pending"})
    cats = await db.entries.distinct("category", {"scope_id": scope_id, "status": "approved"})
    return approved, pending, len(cats)


async def get_pending(scope_id, entry_id):
    return await get_db().entries.find_one({"scope_id": scope_id, "entry_id": entry_id, "status": "pending"})
