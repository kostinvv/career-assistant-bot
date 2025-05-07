import redis

class RedisClient:
    __redis_client = redis.Redis(host='localhost', port=6379)

    @classmethod
    def set_data(cls, key, value):
        cls.__redis_client.set(key, value)

    @classmethod
    def get_data(cls, key):
        return cls.__redis_client.get(key)
    
    @classmethod
    def get_all_keys(cls):
        return cls.__redis_client.keys(pattern='*')