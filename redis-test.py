import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.set('foo', 'bar')
x = r.get('foo')
print(x)