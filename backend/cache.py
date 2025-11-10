import os
import redis
import json
import hashlib

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)  # no ssl param needed

def _hash(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()

def cache_get(query: str):
    key = "cache:query:" + _hash(query)
    value = r.get(key)
    if value:
        return json.loads(value)
    return None

def cache_set(query: str, payload: dict, ttl_seconds=3600):
    key = "cache:query:" + _hash(query)
    r.set(key, json.dumps(payload), ex=ttl_seconds)

def get_session(session_id: str):
    key = f"session:{session_id}"
    v = r.get(key)
    if not v:
        return {"messages": []}
    return json.loads(v)

def append_session_message(session_id: str, role: str, text: str):
    key = f"session:{session_id}"
    ctx = get_session(session_id)
    ctx["messages"].append({"role": role, "text": text})
    r.set(key, json.dumps(ctx), ex=60*60*24)
