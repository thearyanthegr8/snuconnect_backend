from time import sleep
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.set('foo', 'bar')
while True:
    print(r.get('foo'))
    sleep(1)
