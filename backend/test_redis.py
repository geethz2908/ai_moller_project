import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
print("Loaded REDIS_URL:", REDIS_URL)

try:
    print("Connecting to Redis...")
    r = redis.from_url(REDIS_URL, decode_responses=True)
    print("Ping:", r.ping())
except Exception as e:
    print("Error:", e)
