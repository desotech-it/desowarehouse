import redis

# TODO: add error handling
r = redis.Redis(host='redis', decode_responses=True, protocol=3)
