import redis
import json

data = {
    'foo': 'hans',
    'ans': 42,
    "lalala" : "test",
    "bol" : False
}

r = redis.StrictRedis()
#r = redis.Redis(host='localhost', port=6379, db=0)
r.execute_command('JSON.SET', 'object', '.', json.dumps(data))
reply = json.loads(r.execute_command('JSON.GET', 'object'))

print(reply)