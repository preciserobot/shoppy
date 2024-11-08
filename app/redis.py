import json
from redis import Redis
from app.config import REDIS_HOST, REDIS_PORT, REDIS_DB


class DB:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB):
        self.db = Redis(host=host, port=port, db=db, decode_responses=True)

    def set(self, key: str, value: any):
        return self.db.set(key, json.dumps(value))

    def get(self, key: str) -> dict:
        value = self.db.get(key)
        if value:
            return json.loads(value)

    def keys(self, pattern) -> list[str]:
        return self.db.keys(pattern)

    def delete(self, key: str):
        return self.db.delete(key)

    def flush(self):
        return self.db.flushdb()
